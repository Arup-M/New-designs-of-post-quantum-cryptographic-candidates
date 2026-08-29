import os
import secrets
from ..modules.modules import ModuleDSA
import math
try:
    from xoflib import shake256 # type: ignore
except ImportError:
    from ..shake.shake_wrapper import shake256
import random
    
class MLDSA:
    def __init__(self,q,q_len,n,root_of_unity,d,k,l,eta,tau,omega,gamma_1,gamma_2): #defining the parameter set
        self.q = q
        self.q_len = q_len                  # number of bits in q
        self.n = n
        self.root_of_unity = root_of_unity
        self.d = d                          # number of bits dropped from t
        self.k = k                          # Dimensions of A = (k, l)
        self.l = l                          # Dimensions of A = (k, l)
        self.eta = eta                      # Private key range
        self.tau = tau                      # number of ±1 in c
        self.omega = omega                  # Max number of ones in the hint
        self.gamma_1 = gamma_1              # coefficient range of y
        self.gamma_2 = gamma_2              # lower order rounding range
        self.beta = self.tau * self.eta
        #self.c_tilde_bytes = c_tilde_bytes
        self.M = ModuleDSA(self.q,self.n, self.root_of_unity)
        self.R = self.M.ring

        self.random_bytes = os.urandom          # Use system randomness by default, for deterministic randomness

    @staticmethod
    def _h(input_bytes, length):
        """
        H: B^*  -> B^*
        """
        return shake256(input_bytes).read(length)

    def _expand_cap_a_hat(self, rho):
        """
        ExpandA function:
        Construct a matrix from a seed {rho}.
        Parameters:
         rho (bytes): The seed used for generating matrix elements.
        Returns:
         MatrixDilithium: A k x l matrix initialized based on `rho`. Each entry is a polynomial in the NTT domain.
        """
        cap_a_data = [[0 for _ in range(self.l)] for _ in range(self.k)]
        for i in range(self.k):
            for j in range(self.l):
                cap_a_data[i][j] = self.R.rejection_sample_ntt_poly(rho, i, j)
        return cap_a_data, self.M(cap_a_data)

    def _cap_a_prime_hat_matrix(self, rho, t1): # Construct A_prime_hat using A_hat and Identity matrix
        """
        From {cap_a} to {cap_a_prime}:
        """
        cap_a_hat_data = self._expand_cap_a_hat(rho)[0]
        zero_poly = self.R([0]).to_ntt()  # A polynomial with only a zero coefficient
        one_poly = self.R([1]).to_ntt()  # A polynomial with only one coefficient {1}

        # construct Identity matrix
        identity_matrix = [[zero_poly for _ in range(self.k)] for _ in range(self.k)]
        for i in range(self.k):
            identity_matrix[i][i] = one_poly  # Set diagonal to the polynomial '1'

        t1_scale = t1.scale(-(1 << self.d))[1].to_ntt()
        cap_a_prime_hat = [cap_a_hat_data[i] + identity_matrix[i] + t1_scale.data[i] for i in range(self.k)]

        return self.M(cap_a_prime_hat)


    def _expand_s(self, rho_prime):
        """
            ExpandS Function:
            seed: rho_prime
            output vectors s1,s2
        """
        s1_elements = [
            # Our implementation of {rejection_bounded_poly} uses only two values {2,4} of {eta}
            self.R.rejection_bounded_poly(rho_prime, i, self.eta) for i in range(self.l)
        ]
        s2_elements = [
            # Our implementation of {rejection_bounded_poly} uses only two values {2,4} of {eta}
            self.R.rejection_bounded_poly(rho_prime, i, self.eta)
            for i in range(self.l, self.l + self.k)
        ]
        s1 = self.M.vector(s1_elements)
        s2 = self.M.vector(s2_elements)

        return s1_elements,s2_elements,s1, s2



    def _expand_mask_vector(self, rho_prime_2, kappa):
        elements = [
            # Our implementation of {sample_mask_polynomial} uses only two values of {gamma_1}, namely {2^17} and {2^20}
            self.R.sample_mask_polynomial(rho_prime_2, i, kappa, self.gamma_1)
            for i in range(self.k + self.l + 1) #TODO: Shashank
        ]
        return self.M.vector(elements)


    # Storing the pk and sk
    def _pack_pk(self, rho, t1):
        n_bits = self.q_len - self.d
        return rho + t1.bit_pack_t1(n_bits)

    def _unpack_pk(self, pk_bytes):
        rho, t1_bytes = pk_bytes[:32], pk_bytes[32:] #the first 256 bits are rho, and the rest are t1
        n_bits = self.q_len - self.d
        t1 = self.M.bit_unpack_t1(t1_bytes, self.k, 1, n_bits)
        return rho, t1

    def _pack_sk(self, rho, cap_k, tr, s, t0, t1):
        s_bytes = s.bit_pack_s(self.eta)
        # s2_bytes = s2.bit_pack_s(self.eta)
        t0_bytes = t0.bit_pack_t0(self.d)
        t1_bytes = t1.bit_pack_t1(self.q_len - self.d)
        return rho + cap_k + tr + s_bytes + t0_bytes + t1_bytes

    def _unpack_sk(self, sk_bytes): #TODO: fixme
        if self.eta == 2:
            s_bytes = 96
        else: # { for self.eta == 4 }
            s_bytes = 128
        s_len = s_bytes * (self.k + self.l + 1) # note that s = [s1|s2|1]^T, so s_len = s1_len + s2_len +1

        t0_bytes = math.ceil(self.n * self.d / 8)
        t0_len = t0_bytes * self.k

        t1_bytes = math.ceil(self.n * (self.q_len - self.d)/8) #TODO: hardcode for speed up
        t1_len = t1_bytes * self.k
        if len(sk_bytes) != 3 * 32 + s_len + t0_len + t1_len:
            raise ValueError("SK packed bytes is of the wrong length")

        # Split bytes between seeds and vectors
        sk_seed_bytes, sk_vec_bytes = sk_bytes[:96], sk_bytes[96:]

        # Unpack seed bytes
        rho, cap_k, tr = (
            sk_seed_bytes[:32],
            sk_seed_bytes[32:64],
            sk_seed_bytes[64:96],
        )

        # Unpack vector bytes
        s_bytes = sk_vec_bytes[:s_len]
        t0_bytes = sk_vec_bytes[s_len: s_len + t0_len]
        t1_bytes = sk_vec_bytes[s_len + t0_len:]

        # Unpack bytes to vectors
        # s are updated secret consisting of s1 and s2 i.e., s = [s1|s2|1]^T
        s = self.M.bit_unpack_s(s_bytes, self.k + self.l + 1, 1, self.eta) #TODO: Shashank
        t0 = self.M.bit_unpack_t0(t0_bytes, self.k, 1, self.d)
        t1 = self.M.bit_unpack_t1(t1_bytes, self.k, 1, self.q_len - self.d)

        return rho, cap_k, tr, s, t0, t1

    def _pack_h(self, h):
        non_zero_positions = [
            [i for i, c in enumerate(poly.coefficients) if c == 1]
            for row in h.data
            for poly in row
        ]
        packed = []
        offsets = []
        for positions in non_zero_positions:
            packed.extend(positions)
            offsets.append(len(packed))

        padding_len = self.omega - offsets[-1]
        packed.extend([0 for _ in range(padding_len)])
        return bytes(packed + offsets)

    def _unpack_h(self, h_bytes):
        offsets = [0] + list(h_bytes[-self.k :])
        non_zero_positions = [
            list(h_bytes[offsets[i] : offsets[i + 1]]) for i in range(self.k)
        ]

        matrix = []
        for poly_non_zero in non_zero_positions:
            coefficients = [0 for _ in range(256)]
            for non_zero in poly_non_zero:
                coefficients[non_zero] = 1
            matrix.append([self.R(coefficients)])
        return self.M(matrix)

    def _pack_sig(self, c_tilde, z, h):
        return c_tilde + z.bit_pack_z(self.gamma_1) + self._pack_h(h)

    def _unpack_sig(self, sig_bytes):
        c_tilde = sig_bytes[:32]
        z_bytes = sig_bytes[32 : -(self.k + self.omega)]
        h_bytes = sig_bytes[-(self.k + self.omega) :]

        z = self.M.bit_unpack_z(z_bytes, self.k+self.l +1, 1, self.gamma_1)
        h = self._unpack_h(h_bytes)
        return c_tilde, z, h
#######################################

    def keygen(self, zeta: bytes = None):
        """
            :Generates a public-private keypair
        """
        # Random seed
        if zeta is None:
            zeta = secrets.token_bytes(32) #{32*8 = 256} bit seed
        elif not (isinstance(zeta, (bytes, bytearray)) and len(zeta) == 32):
            raise ValueError("expected a 32-bytes bytestring.")

        # Expand with an XOF (SHAKE256)
        seed_bytes = self._h(zeta, 128)

        # Split bytes into suitable chunks
        rho, rho_prime, cap_k = seed_bytes[:32], seed_bytes[32:96], seed_bytes[96:]

        # Generate matrix A ∈ R^(kxl) in the NTT domain
        cap_a_hat = self._expand_cap_a_hat(rho)[1]
        # print(a_hat)

        # Generate the error vectors s1 ∈ R^l, s2 ∈ R^k
        s1_list, s2_list, s1, s2 = self._expand_s(rho_prime)

        #new secret vector
        s = self.M([[elt] for elt in s1_list + s2_list + [self.R([1])]])  # {s = [s1 | s2 | 1]^T}

        s1_hat = s1.to_ntt()

        # Matrix multiplication
        t = (cap_a_hat @ s1_hat).from_ntt() + s2
        t1, t0 = t.power_2_round(self.d)

        # Pack up the bytes
        pk = self._pack_pk(rho, t1)
        tr = self._h(pk, 32)

        sk = self._pack_sk(rho, cap_k, tr, s, t0, t1)
        return pk, sk

    def sign(self, sk_bytes, msg, random_bit: bool = None):
        """
            :Generates a signature for a message m from a byte-encoded private key
        """
        # unpack the secret key
        rho, cap_k, tr, s, t0, t1 = self._unpack_sk(sk_bytes)
        cap_a_prime_hat = self._cap_a_prime_hat_matrix(rho, t1)  #  (A|I)

        mu = self._h(tr + msg, 64) # Set seeds and nonce (kappa)
        kappa = 0
        rho_prime_2 = self._h(cap_k + mu, 64)

        # Precompute NTT representation
        s_hat = s.to_ntt()
        t0_hat = t0.to_ntt()

        alpha = self.gamma_2 << 1
        count = 0
        while True:
            count += 1
            y = self._expand_mask_vector(rho_prime_2, kappa)
            y_hat = y.to_ntt()
            kappa += self.k + self.l + 1 #TODO: Shashank
            w = (cap_a_prime_hat @ y_hat).from_ntt()
            w1, w0 = w.decompose(alpha)
            #####################################################

            w1_bytes = w1.bit_pack_w(self.gamma_2)
            c_tilde = self._h(mu + w1_bytes, 32)
            c = self.R.sample_in_ball(c_tilde, self.tau)

            # Store c in NTT form
            c_hat = c.to_ntt()
            
            if random_bit is None:
                bit = random.randint(0, 1)
            else:
                bit = random_bit
            
            if bit:
                z = y - (s_hat.scale(c_hat)[1]).from_ntt()
            else:
                z = y + (s_hat.scale(c_hat)[1]).from_ntt()

            if not (z.check_norm_bound(self.gamma_1 - self.beta)):
                c_t0 = t0_hat.scale(c_hat)[1].from_ntt()
                #makehint
                if bit:
                    if not (-c_t0).check_norm_bound(self.gamma_2):
                        h = (c_t0).make_hint(w-c_t0, alpha)
                else:
                    if not c_t0.check_norm_bound(self.gamma_2):
                        h = (-c_t0).make_hint(w+c_t0, alpha)

                # if not c_t0.check_norm_bound(self.gamma_2):
                #     #makehint
                #     if bit:
                #         h = (c_t0).make_hint(w-c_t0, alpha)
                #     else:
                #         h = -c_t0.make_hint(w+c_t0, alpha)

                if h.sum_hint() <= self.omega:
                    return  self._pack_sig(c_tilde, z, h), count


    def verify(self, pk_bytes, m, sig_bytes):
        """
        Verifies a signature for a message m from a byte-encoded public key and
        signature
        """
        rho, t1 = self._unpack_pk(pk_bytes)
        c_tilde, z, h = self._unpack_sig(sig_bytes)
        if h.sum_hint() > self.omega:
            return False
        if z.check_norm_bound(self.gamma_1 - self.beta):
            return False

        cap_a_prime_hat = self._cap_a_prime_hat_matrix(rho, t1)
        tr = self._h(pk_bytes, 32) #Compute trace {tr}
        mu = self._h(tr + m, 64)

        z_hat = z.to_ntt()
        cap_a_prime_z = (cap_a_prime_hat @ z_hat).from_ntt()
        w_prime = h.use_hint(cap_a_prime_z, 2 * self.gamma_2)
        w_prime_bytes = w_prime.bit_pack_w(self.gamma_2)
        return c_tilde == self._h(mu + w_prime_bytes, 32)
