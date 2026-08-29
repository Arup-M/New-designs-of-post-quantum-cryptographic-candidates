from .polynomials_generic import PolynomialRing, Polynomial
import random
import math
from ..utilities.utils import *
from ..shake.shake_wrapper import shake128, shake256

class PolynomialRingDSA(PolynomialRing):
    """
    Represents a polynomial ring R = GF(q)[X] / (X^n + 1) adapted
    for Dilithium cryptography.
    """
    def __init__(self, q, n, root_of_unity):
        """
        Initialize the polynomial ring with generic parameters.
        q: Prime modulus
        n: Degree of the polynomial (usually a power of 2)
        root_of_unity: Primitive n-th root of unity mod q
        """
        assert n & (n-1) == 0, "n must be a power of 2"
        assert (q - 1) % (2*n) == 0, "q - 1 must be divisible by 2*n"
        assert pow(root_of_unity, 2*n, q) == 1 and pow(root_of_unity, n, q) != 1, "Invalid root of unity"

        # Initialize parent class
        super().__init__(q, n)

        self.q = q
        self.n = n
        self.root_of_unity = root_of_unity

        self.element = PolynomialDSA
        self.element_ntt = PolynomialNTT

        # Precompute zetas for NTT
        k = len(bin(self.n)[3:])
        self.ntt_zetas = [
                pow(root_of_unity, self.br(i, k), q) for i in range(self.n)
            ]

        #assert gcd(n, q) == 1, "n must be coprime with q"
        self.ntt_f = pow(n, -1, q)

    @staticmethod
    def br(i, k):
        """
        The Bit reversal of an unsigned k-bit integer.
        """
        assert 0 <= i < 2 ** k, "i must be a non-negative integer within k bits"
        assert k > 0, "k must be positive"
        bin_i = bin(i)[2:].zfill(k)
        return int(bin_i[::-1], 2)

    def sample_in_ball(self, seed, tau):
        """
            Create a random 256-element array with τ ±1’s and (256 − τ) 0′s using
            the input seed ρ (and an SHAKE256) to generate the randomness needed
        """

        def rejection_sample(i_value, xof_bytes):
            """
                Sample random bytes from `xof_bytes` and
                interpret them as integers in {0, ..., 255}

                Rejects values until a value {j <= i} is found
            """
            while True:
                j_value = xof_bytes.read(1)[0] # read integer stored in one byte
                if j_value <= i_value:
                    return j_value

        # Initialise the XOF
        xof = shake256(seed)

        # Set the first 8 bytes for the sign and leave the rest for
        # sampling.
        sign_bytes = xof.read(8)
        sign_int = int.from_bytes(sign_bytes, "little")

        # Set the list of coefficients to be 0
        coefficients = [0 for _ in range(256)]

        # Now set tau values of coefficients to be ±1
        for i in range(256 - tau, 256):
            j = rejection_sample(i, xof)
            coefficients[i] = coefficients[j]
            coefficients[j] = 1 - 2 * (sign_int & 1)
            sign_int >>= 1

        return self(coefficients)



    def __call__(self, coefficients, is_ntt=False):
        if not is_ntt:
            element = self.element
        else:
            element = self.element_ntt

        if isinstance(coefficients, int):
            return element(self, [coefficients])
        if not isinstance(coefficients, list):
            raise TypeError(
                f"Polynomials should be constructed from a list of integers, of length at most d = {256}"
            )
        return element(self, coefficients)

    def random_element(self):
        """Generate a random polynomial in the ring."""
        coefficients = [random.randint(0, self.q - 1) for _ in range(self.n)]
        return self(coefficients, is_ntt=False)

    # Singh: This function will be used in expandA function for generating i,j poly of matrix A
    def rejection_sample_ntt_poly(self, rho, i, j):
        """
        Samples an element in the NTT domain of R^q using rejection sampling
        """
        def rejection_sample(out_xof):
            """
            Sample three random bytes from `xof` and
            interpret them as integers in {0, ..., 2^23-1}

            Rejects values until a value j < q is found
            """
            max_attempts = 1000
            for _ in range(max_attempts):
                j_bytes = out_xof.read(3) ## read 3 bytes of out_xof
                if len(j_bytes) != 3:
                    raise ValueError("Failed to read 3 bytes from XOF.")
                j_value = int.from_bytes(j_bytes, "little")
                j_value &= 0x7FFFFF
                if j_value < self.q:
                    return j_value
            raise RuntimeError("Rejection sampling failed after maximum attempts.")

        # Initialise the XOF
        seed = rho + bytes([j, i]) #to the seed rho, add the bytes {[j, i]}, can use [i,j] as well
        xof = shake128(seed)
        coefficients = [rejection_sample(xof) for _ in range(256)]
        return self(coefficients, is_ntt=True)

    # Singh: This function will be used in the ExpandS(rho_prime), which returns a vector of polynomials
    # whose coefficients are bounded by eta
    def rejection_bounded_poly(self, rho_prime, i, eta):
        """
            Computes an element of the polynomial ring with coefficients between
            {-eta} and {eta} using rejection sampling from an XOF
            This function is used in the ExpandS(rho_prime) function. It is very specific to the new signature
            algorithm.
            Only two values ({2,4}) of {eta} are used in the algorithm.
        """
        def coefficient_from_half_byte(j_value, eta_value):
            """
            Rejects values until a value j_value < 2η is found
            """
            if eta_value == 2 and j_value < 15:
                return 2 - (j_value % 5)
            elif j_value < 9:
                assert eta_value == 4
                return 4 - j_value
            return False

        # Initialize the XOF using {rho_prime} and {i} i.e., for {i}^th component (polynomial) of vector
        seed = rho_prime + int.to_bytes(i, 2, "little")
        xof = shake256(seed)

        # Sample bytes for all self.n coefficients
        index = 0
        coefficients = [0 for _ in range(256)]
        while index < 256:
            # Consider two values for each byte (top and bottom four bits)
            j = xof.read(1)[0] # read one byte of out_xof and convert to int

            c0 = coefficient_from_half_byte(j % 16, eta) # try to generate one coefficient from lower 4 bits
            if c0 is not False:
                coefficients[index] = c0
                index += 1

            c1 = coefficient_from_half_byte(j // 16, eta) #try to generate one coefficient from the upper 4 bits
            if c1 is not False and index < 256:
                coefficients[index] = c1
                index += 1
        return self(coefficients)

    def sample_mask_polynomial(self, rho_prime, i, kappa, gamma_1):
        """
            This function is defined only for two values of {gamma_1} namely {2**17} and {2**19}
            Samples an element in the polynomial ring with elements bounded
            between {-gamma_1 + 1} and {gamma_1}.

            {gamma_1} is always set to be a power of 2.
        """
        if gamma_1 == (1 << 17):
            bit_count = 18
            total_bytes = math.ceil(self.n * bit_count / 8)   # 576 = (256 * 18) / 8
        else: # {gamma_1 = (1 << 19)} i.e., 2**19
            bit_count = 20
            total_bytes = math.ceil(self.n * bit_count / 8)  # (256 * 20) / 8 = 640

        # Initialise the XOF
        seed = rho_prime + int.to_bytes(kappa + i, 2, "little")
        xof_bytes = shake256(seed).read(total_bytes)
        r = int.from_bytes(xof_bytes, "little")
        mask = (1 << bit_count) - 1
        coefficients = [gamma_1 - ((r >> bit_count * i) & mask) for i in range(self.n)]

        return self(coefficients)

    ## bit unpacking can be kept more suitably here.
    def __bit_unpack(self, input_bytes, n_bits):
        # Validate input types and values
        if not isinstance(input_bytes, (bytes, bytearray)):
            raise TypeError("input_bytes must be of type bytes or bytearray")
        if len(input_bytes) == 0:
            raise ValueError("input_bytes cannot be empty")
        if n_bits <= 0:
            raise ValueError("n_bits must be a positive integer")
        if (len(input_bytes) * 8) <  (n_bits * self.n): ## it is not clear
            raise ValueError(
                f"Input bytes length ({len(input_bytes)} bytes) times 8 must be ge to {n_bits * self.n}"
            )
        # Convert bytes to an integer
        r = int.from_bytes(input_bytes, "little")
        mask = (1 << n_bits) - 1

        # Unpack bits into a list
        try:
            return [(r >> n_bits * i) & mask for i in range(self.n)]
        except AttributeError:
            raise AttributeError("self.n is not defined or initialized")

    def bit_unpack_t0(self, input_bytes, d): # d is the bit size of coefficients
        altered_coefficients = self.__bit_unpack(input_bytes, d)
        coefficients = [(1 << 12) - c for c in altered_coefficients]
        return self(coefficients)

    def bit_unpack_t1(self, input_bytes, n_bits): # {n_bits = 10} i.e., 23 -13
        coefficients = self.__bit_unpack(input_bytes, n_bits)
        return self(coefficients)

    # We only consider two values for the bound {eta} for the coefficients of S i.e., {eta =2} and {eta =4}
    def bit_unpack_s(self, input_bytes, n_bits_eta): #secret vectors have coefficient at most eta
        altered_coefficients = self.__bit_unpack(input_bytes, n_bits_eta)
        # Level 2 and 5 parameter set
        if n_bits_eta == 3:
            eta = 2
            coefficients = [eta - c for c in altered_coefficients]
            return self(coefficients)
        else:
            if n_bits_eta == 4:
                eta = 4
                coefficients = [eta - c for c in altered_coefficients]
                return self(coefficients)
            else:
                raise ValueError(f"n_bits_eta must be 3 or 4, got {n_bits_eta}")

    def bit_unpack_w(self, input_bytes, n_bits_gamma_2):
        if n_bits_gamma_2 == 6:
            #gamma_2 = 95232
            coefficients = self.__bit_unpack(input_bytes, n_bits_gamma_2)
            return self(coefficients)
        else:
            if n_bits_gamma_2 == 4:
                #gamma_2 = 261888
                coefficients = self.__bit_unpack(input_bytes, n_bits_gamma_2)
                return self(coefficients)
            else:
                raise ValueError(f"Expected gamma_2 to be either (q-1)/88 or (q-1)/32, got {n_bits_gamma_2 = }")


    def bit_unpack_z(self, input_bytes, n_bits_gamma_1):
        if n_bits_gamma_1 == 18:
            gamma_1 = (1 << 17)
            altered_coefficients = self.__bit_unpack(input_bytes, n_bits_gamma_1)
            coefficients = [gamma_1 - c for c in altered_coefficients]
            return self(coefficients)
        else:
            if n_bits_gamma_1 == 20:
                gamma_1 = (1 << 19)
                altered_coefficients = self.__bit_unpack(input_bytes, n_bits_gamma_1)
                coefficients = [gamma_1 - c for c in altered_coefficients]
                return self(coefficients)
            else:
                raise ValueError(f"n_bits_gamma_1 must be 18 or 20, got {n_bits_gamma_1}")


class PolynomialDSA(Polynomial):
    def __init__(self, parent, coefficients_list):
        super().__init__(parent, coefficients_list)  # Initialize the base class
        self.parent = parent
        self.coefficients = self._parse_coefficients(coefficients_list)

    def to_ntt(self): # FIPS-204: Algorithm 41
        """
        Convert a polynomial to number-theoretic transform (NTT)
        """
        k = 0
        l = self.parent.n // 2

        coefficients = self.coefficients[:]
        zetas = self.parent.ntt_zetas
        while l > 0:
            start = 0
            while start < self.parent.n:
                k = k + 1
                zeta = zetas[k]
                for j in range(start, start + l):
                    t = (zeta * coefficients[j + l]) % self.parent.q
                    coefficients[j + l] = (coefficients[j] - t) % self.parent.q
                    coefficients[j] = (coefficients[j] + t) % self.parent.q
                start = start + 2*l # l + (j + 1)
            l >>= 1
        return self.parent(coefficients, is_ntt=True)

    def from_ntt(self):
        raise TypeError(f"Polynomial is of type: {type(self)}")

    def power_2_round(self, d):
        power_2 = 1 << d
        r1_coefficients = []
        r0_coefficients = []
        for c in self.coefficients:
            r = c % self.parent.q
            r0 = reduce_mod_pm(r, power_2)
            r1_coefficients.append((r - r0) >> d)
            r0_coefficients.append(r0)

        r1_poly = self.parent(r1_coefficients)
        r0_poly = self.parent(r0_coefficients)

        return r1_poly, r0_poly

    ##########################################################

    def high_bits(self, alpha, is_ntt=False):
        """
        Extract the higher significant bits of coefficients and forms a new polynomial
        with the same degree as the original polynomial.
        Parameters:
        alpha : int
            Controls the splitting of bits.
        is_ntt : bool (optional)
            Indicates whether the coefficients are in the Number Theoretic Transform
            (NTT) domain. Defaults to False.

        Returns:
        RingElement
            A new RingElement with the same NTT form object with coefficients containing the higher bits
            obtained after processing with the alpha parameter.
        """
        # high_bits function is defined in module utilities
        new_coefficients = [high_bits(c, alpha, self.parent.q) for c in self.coefficients]
        return self.parent(new_coefficients, is_ntt=is_ntt)

    def low_bits(self, alpha, is_ntt=False):
        # low_bits function is defined in module utilities
        new_coefficients = [low_bits(c, alpha, self.parent.q) for c in self.coefficients]
        return self.parent(new_coefficients, is_ntt=is_ntt)

    ## The following also return high_bits and low_bits polynomials
    #  Dr Singh
    ## We could define high_bits and low_bits using decompose function do it later and check the result
    def decompose(self, alpha):
        coefficients_high = []
        coefficients_low = []
        for c in self.coefficients:
            r1, r0 = decompose(c, alpha, self.parent.q)
            coefficients_high.append(r1)
            coefficients_low.append(r0)
        return self.parent(coefficients_high), self.parent(coefficients_low)



    def check_norm_bound(self, bound):
        """
        It returns true if the inf norm of polynomial coefficient
        is greater or equal to the bound.
        """
        return any(check_norm_bound(c, bound, self.parent.q) for c in self.coefficients)

    ######################################################################################

    """
    Function specific to Dilithium type signature.
    will be presented below.
    """

    @staticmethod
    def __bit_pack(coefficients, n_bits, n_bytes):  ## endianness="little"
        """
        It packs the coefficients into a bit-packed byte array.

        Args:
            coefficients (list[int]): List of coefficients to pack.
            {n_bits} (int): Number of bits allocated per coefficient.
            {n_bytes} (int): Number of bytes in the output.

        Returns:
            bytes: Bit-packed representation of the coefficients.

        Raises:
            ValueError: If coefficients don't fit in the specified n_bits,
                        or the packed result doesn't fit in n_bytes.
        """
        # Validate coefficients fit within n_bits
        # We have assumed all the coefficients are positive here, so we can use 0 <= c < (1 << n_bits)
        assert all(0 <= c < (1 << n_bits) for c in coefficients), \
            f"All coefficients must fit within {n_bits} bits"

        # Validate total bits required fits within n_bytes
        total_bits = len(coefficients) * n_bits
        assert total_bits <= n_bytes * 8, \
            f"Not enough bytes ({n_bytes}) to store all coefficients"

        r = 0
        # Look at the polynomial {[f_0,.., f_{n-1}]} as an integer in the base {2^n_bits}
        for c in reversed(coefficients): # r = [f_{n-1}, f_{n-2}, ...,f_2, f_1, f_0]_{2^n_bits}
            r <<= n_bits
            r |= c

        # Convert to bytes and return
        return r.to_bytes(n_bytes, 'little')   #endianness)


    ######################################################################################

    # Coefficients of t0 are in the range {[-2^{d-1} + 1  ...  2^{d-1}]} i.e., they could be negative
    def bit_pack_t0(self, d): #d: number of bits dropped from t (13 in this case)
        # 416 = 256 * 13 // 8
        n_bytes = math.ceil(self.parent.n * d / 8)  # compute the number of bytes to store the {self.parent.n} coefficients of {d} bit each
        altered_coefficients = [(1 << (d-1)) - c for c in self.coefficients] # we are encoding the coefficients to be positive so that {__bit_pack} can be called.
        return self.__bit_pack(altered_coefficients, d, n_bytes)


    def bit_pack_t1(self, n_bits): # n_bits: coefficient size of t1 is at most n_bits (23-10 = 13)
        # 320 = 256 * 10 // 8
        n_bytes = math.ceil(self.parent.n * n_bits / 8) #minimum bytes require to pack t1
        return self.__bit_pack(self.coefficients, n_bits, n_bytes)

    def bit_pack_w(self, n_bits_gamma_2):
        n_bytes = math.ceil(self.parent.n * n_bits_gamma_2 / 8)
        return self.__bit_pack(self.coefficients, n_bits_gamma_2, n_bytes)

    # We only consider two values for the bound {eta} for the coefficients of S i.e., {eta =2} and {eta =4}
    def bit_pack_s(self, n_bits_eta): #packing of secret vectors s1 and s2
        # we update the coefficients to make them positive in the range {[0  ...  2 * eta]}
        if n_bits_eta == 3:
            eta = 2
            n_bytes = math.ceil(self.parent.n * n_bits_eta / 8) ## TODO: we can hardcode this for speed up
            altered_coefficients = [self._sub_mod_q(eta, c) for c in self.coefficients] # {_sub_mod_q} is useless here.
            return self.__bit_pack(altered_coefficients, n_bits_eta, n_bytes)
        else:
            if n_bits_eta == 4:
                eta = 4
                n_bytes = math.ceil(self.parent.n * n_bits_eta / 8)
                altered_coefficients = [self._sub_mod_q(eta, c) for c in self.coefficients]  # {_sub_mod_q} is useless here.
                return self.__bit_pack(altered_coefficients, n_bits_eta, n_bytes)
            else:
                ValueError(f"Expected eta to be either 2 or 4")
                return None

    def bit_pack_z(self, n_bits_gamma_1):
        if n_bits_gamma_1 == 18:
            gamma_1 = (1 << 17)
            n_bytes = math.ceil(self.parent.n * n_bits_gamma_1 / 8)
            altered_coefficients = [self._sub_mod_q(gamma_1, c) for c in self.coefficients]
            return self.__bit_pack(altered_coefficients, n_bits_gamma_1, n_bytes)
        else:
            if n_bits_gamma_1 == 20:
                gamma_1 = (1 << 19)
                n_bytes = math.ceil(self.parent.n * n_bits_gamma_1 / 8)
                altered_coefficients = [self._sub_mod_q(gamma_1, c) for c in self.coefficients]
                return self.__bit_pack(altered_coefficients, n_bits_gamma_1, n_bytes)
            else:
                ValueError(f"Expected n_bits_gamma_1 to be either 18 or 20")
                return None


    def make_hint(self, other, alpha):
        coefficients = [
            make_hint(r, z, alpha, self.parent.q) for r, z in zip(self.coefficients, other.coefficients)
        ]
        return self.parent(coefficients)

    def use_hint(self, other, alpha):
        coefficients = [
            use_hint(h, r, alpha, self.parent.q) for h, r in zip(self.coefficients, other.coefficients)
        ]
        return self.parent(coefficients)


class PolynomialNTT(PolynomialDSA):
    def __init__(self, parent, coefficients_list):
        super().__init__(parent, coefficients_list)
        self.parent = parent
        self.coefficients = self._parse_coefficients(coefficients_list)

    def to_ntt(self):
        raise TypeError(f"Polynomial is of type: {type(self)}")

    def from_ntt(self):
        """
        Convert a polynomial from {number-theoretic} transform (NTT) form in place
        The input is in bit-reversed order, the output is in standard order.
        """
        l, k = 1, self.parent.n
        coefficients = self.coefficients[:]
        zetas = self.parent.ntt_zetas
        while l < self.parent.n:
            start = 0
            while start < self.parent.n:
                k = k - 1
                zeta = -zetas[k]
                for j in range(start, start + l):
                    t = coefficients[j]
                    coefficients[j] = (t + coefficients[j + l]) % self.parent.q
                    coefficients[j + l] = (t - coefficients[j + l]) % self.parent.q
                    coefficients[j + l] = (zeta * coefficients[j + l]) % self.parent.q
                start = start + 2*l
            l = l << 1

        for j in range(self.parent.n):
            coefficients[j] = (coefficients[j] * self.parent.ntt_f) % self.parent.q

        return self.parent(coefficients, is_ntt=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(coefficients={self.coefficients})"

    def ntt_coefficient_multiplication(self, f_coefficients, g_coefficients):
        return [(c1 * c2) % self.parent.q for c1, c2 in zip(f_coefficients, g_coefficients)]

    def ntt_multiplication(self, other):
        """
        Number Theoretic Transform multiplication.
        """
        if not isinstance(other, type(self)):
            raise ValueError

        new_coefficients = self.ntt_coefficient_multiplication(self.coefficients, other.coefficients)
        return new_coefficients

    def __mul__(self, other):
        if isinstance(other, type(self)):
            new_coefficients = self.ntt_multiplication(other)
        elif isinstance(other, int):
            new_coefficients = [(c * other) % self.parent.q for c in self.coefficients]
        else:
            raise NotImplementedError(
                f"Polynomials can only be multiplied by each other, or scaled by integers, {type(other) = }, {type(self) = }"
            )
        return self.parent(new_coefficients, is_ntt=True)

    def __add__(self, other):
        new_coefficients = self._add_(other)
        return self.parent(new_coefficients, is_ntt=True)

    def __sub__(self, other):
        new_coefficients = self._sub_(other)
        return self.parent(new_coefficients, is_ntt=True)


