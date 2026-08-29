import os
import random
import secrets

from .conversion import Conversion
from .sample import Sample
from .ntt import NTT
from .encode import Encode
from .operation import Operations


class DSA:
    def __init__(self, default_parameters: dict):
        self.q = default_parameters["q"]
        self.d = default_parameters["d"]
        self.N = default_parameters["N"]

        self.k = default_parameters["k"]
        self.l = default_parameters["l"]
        self.eta = default_parameters["eta"]
        self.gamma1 = default_parameters["gamma1"]
        self.gamma2 = default_parameters["gamma2"]
        self.tau = default_parameters["tau"]
        self.omega = default_parameters["omega"]

        self.beta = self.tau * self.eta

        # ! initialize all other classes here later.
        self.convert = Conversion(self.q, self.N)
        self.sample = Sample(self.q, self.N, self.eta, self.gamma1, self.k, self.l, self.tau, self.omega)
        self.ntt = NTT(self.N, self.q, self.d)
        self.encode = Encode(self.d, self.N, self.q, self.eta, self.k, self.l, self.gamma1, self.gamma2, self.omega)
        self.operation = Operations(self.q, self.N, self.gamma2)

        self.random_bytes = os.urandom  # Use system randomness by default, for deterministic randomness

        # self.test_vec1 = None
        # self.test_vec2 = None

        self.total_num_of_rejections = 0

        if self.q == 8380417:
            self.ZETAS = [0, 4808194, 3765607, 3761513, 5178923, 5496691, 5234739, 5178987,
                          7778734, 3542485, 2682288, 2129892, 3764867, 7375178, 557458, 7159240,
                          5010068, 4317364, 2663378, 6705802, 4855975, 7946292, 676590, 7044481,
                          5152541, 1714295, 2453983, 1460718, 7737789, 4795319, 2815639, 2283733,
                          3602218, 3182878, 2740543, 4793971, 5269599, 2101410, 3704823, 1159875,
                          394148, 928749, 1095468, 4874037, 2071829, 4361428, 3241972, 2156050,
                          3415069, 1759347, 7562881, 4805951, 3756790, 6444618, 6663429, 4430364,
                          5483103, 3192354, 556856, 3870317, 2917338, 1853806, 3345963, 1858416,
                          3073009, 1277625, 5744944, 3852015, 4183372, 5157610, 5258977, 8106357,
                          2508980, 2028118, 1937570, 4564692, 2811291, 5396636, 7270901, 4158088,
                          1528066, 482649, 1148858, 5418153, 7814814, 169688, 2462444, 5046034,
                          4213992, 4892034, 1987814, 5183169, 1736313, 235407, 5130263, 3258457,
                          5801164, 1787943, 5989328, 6125690, 3482206, 4197502, 7080401, 6018354,
                          7062739, 2461387, 3035980, 621164, 3901472, 7153756, 2925816, 3374250,
                          1356448, 5604662, 2683270, 5601629, 4912752, 2312838, 7727142, 7921254,
                          348812, 8052569, 1011223, 6026202, 4561790, 6458164, 6143691, 1744507,
                          1753, 6444997, 5720892, 6924527, 2660408, 6600190, 8321269, 2772600,
                          1182243, 87208, 636927, 4415111, 4423672, 6084020, 5095502, 4663471,
                          8352605, 822541, 1009365, 5926272, 6400920, 1596822, 4423473, 4620952,
                          6695264, 4969849, 2678278, 4611469, 4829411, 635956, 8129971, 5925040,
                          4234153, 6607829, 2192938, 6653329, 2387513, 4768667, 8111961, 5199961,
                          3747250, 2296099, 1239911, 4541938, 3195676, 2642980, 1254190, 8368000,
                          2998219, 141835, 8291116, 2513018, 7025525, 613238, 7070156, 6161950,
                          7921677, 6458423, 4040196, 4908348, 2039144, 6500539, 7561656, 6201452,
                          6757063, 2105286, 6006015, 6346610, 586241, 7200804, 527981, 5637006,
                          6903432, 1994046, 2491325, 6987258, 507927, 7192532, 7655613, 6545891,
                          5346675, 8041997, 2647994, 3009748, 5767564, 4148469, 749577, 4357667,
                          3980599, 2569011, 6764887, 1723229, 1665318, 2028038, 1163598, 5011144,
                          3994671, 8368538, 7009900, 3020393, 3363542, 214880, 545376, 7609976,
                          3105558, 7277073, 508145, 7826699, 860144, 3430436, 140244, 6866265,
                          6195333, 3123762, 2358373, 6187330, 5365997, 6663603, 2926054, 7987710,
                          8077412, 3531229, 4405932, 4606686, 1900052, 7598542, 1054478, 7648983]
        else:
            self.ZETAS = [0, 3546050, 4666247, 1430380, 1488760, 238876, 2408293, 2487910, 2999819,
                          778454, 1592971, 1843795, 191805, 6041169, 4987173, 4358375, 3496061,
                          5381454, 2607033, 3229103, 7230578, 3810701, 1231173, 6901521, 6677695,
                          7402602, 5578487, 5400329, 228951, 6235301, 379671, 2700573, 6821699, 6088323,
                          2017658, 3517119, 5043283, 7879438, 4415380, 3289798, 361173, 285609, 6401039,
                          7276582, 8081487, 1076249, 6656961, 6800432, 2975576, 6567999, 4567516, 7635448,
                          7486759, 7961200, 3357370, 776111, 3643818, 7795782, 6746163, 4129073, 7574027,
                          4923143, 6189369, 5410230, 1432691, 7970039, 2529962, 7350953, 5781780, 4707358,
                          5823156, 6631169, 1280101, 3347577, 6387980, 1419379, 3294813, 6028690, 6251112,
                          5976656, 942678, 1218974, 2012100, 4153858, 90213, 2635388, 4390943, 208252,
                          3550225, 7900664, 8166658, 6509574, 3646527, 6566838, 5307874, 5856575, 7504188,
                          602253, 3149544, 6756334, 5267101, 4411219, 4577273, 7786195, 3598485, 8112707,
                          3965360, 6999948, 4703397, 7425223, 836558, 4063717, 1347115, 8346572, 6124738,
                          91473, 7538353, 1600964, 5051475, 8331653, 7969515, 1571667, 1832824, 2464928,
                          4261595, 3183020, 2208987, 6719777, 11998, 7684714, 691964, 697257, 5310910, 7264499,
                          5196320, 4723340, 1510085, 684346, 6494627, 6208428, 4200404, 6683257, 3140661, 3962357,
                          3144411, 5436303, 384475, 2675125, 130672, 5625081, 8289525, 728105, 6363726, 1736330,
                          5294339, 5544350, 5553195, 5269051, 3058131, 7673358, 7124984, 2359697, 4727941, 4293625,
                          5669321, 5275160, 462249, 1530192, 7473330, 6273270, 6906682, 7159879, 6630741, 2262442,
                          718375, 3468188, 4064686, 6438891, 6572864, 3720801, 5433336, 5387423, 7444104, 6106988,
                          7016718, 7589152, 6260868, 2581353, 4538675, 6189709, 7487189, 6967702, 3274168, 2452388,
                          6253896, 2429814, 4808454, 7699380, 6611851, 1455052, 99950, 7316536, 1127602, 2843083,
                          3015739, 7863017, 2149182, 3937271, 923983, 4445236, 5110969, 6529668, 905493, 5248205,
                          689238, 327774, 7475430, 56549, 5726741, 1285328, 5985344, 892702, 2889808, 5165541,
                          4959253, 7647465, 3843989, 2540191, 8321205, 839505, 6268504, 1549683, 8038169, 3951296,
                          89205, 7966791, 2092747, 4871440, 1986551, 6488031, 7702467, 1394751, 3325439, 7639484,
                          4079962, 1792773, 3355069, 6833347, 4548925, 2393905, 330705, 5640441, 8100888, 3081565,
                          3217297, 8254222]

    def dsa_keygen(self, random_seed: bytes = None) -> tuple[bytes, bytes]:
        """
        Generates a public-private key pair from a seed. Can take an input seed for deterministic output.
        Args:
            random_seed (bytes): for deterministic output 32 bytes input bytestring.
        Returns:
            ( public_key, private_key ) (Tuple[ bytes, bytes]): Tuple of key pair containing public key and private key.
        Raises:
            ValueError: If the input seed is not 32 bytes.
            TypeError: If the input seed is not a byte string.
        """
        # line 1: choose random 32-byte seed
        if random_seed is None:
            random_seed = secrets.token_bytes(32)
        elif not (isinstance(random_seed, (bytes, bytearray)) and len(random_seed) == 32):
            raise ValueError("expected a 32-bytes bytestring.")

        # line 2: expand the hashed random seed into 3 different parts.
        seed = self.convert.hash(random_seed, 128)
        rho = seed[0:32]  # a. Get ρ (rho):           The first 32 bytes
        rho_prime = seed[32:96]  # b. Get ρ' (rho_prime):    The next 64 bytes
        k_seed = seed[96:]  # c. Get k_seed:            The last 32 bytes

        # line 3: generate the matrix A (k x l) and store polynomials as list of coefficients.
        matrix_a_cap = self.sample.gen_a(rho)

        # line 4: generate and store s and e polynomial vectors.
        s1, s2 = self.sample.gen_s(rho_prime)

        # line 5 compute: vector t as 'A.s + e'.
        # a. Transform s into the NTT domain for faster polynomial multiplication.
        s1_ntt = [self.ntt.ntt(p) for p in s1]
        # b. Compute the matrix-vector product Â ◦ NTT(s)
        a_s1_ntt = self.ntt.multiply_ntt_matrix_vector(matrix_a_cap, s1_ntt)
        # c. Transform the result back from the NTT domain to the standard polynomial form.
        a_s1 = [self.ntt.inv_ntt(p) for p in a_s1_ntt]
        # d. Add the second secret vector e
        t = self.ntt.add_vector_ntt(a_s1, s2)

        # line 6: decompose t into (t1, t0) such that t = (t1.2^d + t0) mod q
        t1, t0 = self.ntt.power2round_vec(t)

        # encode public_key
        public_key = self.encode.byte_pack_pk(rho, t1)

        # line 8: hash public_key to make tr
        tr = self.convert.hash(public_key, 32)

        # concatenating to obtain the secret vector
        poly = [1 if i == 0 else 0 for i in range(self.N)]
        s = s1 + s2 + [poly]

        # encode private_key
        private_key = self.encode.byte_pack_sk(rho, k_seed, tr, s, t0, t1)

        # line 10: return both public and private keys.
        return public_key, private_key

    def dsa_sign(self, private_key: bytes, message, random_bit: bool = None):
        """
        Algorithm to generate a signature for a message.
        Args:
            private_key (bytes): The private key bytestring.
            message (bytes): The message to be signed in bytes.
            random_bit: random bit used for randomizing the signature
        Returns:
            signature (bytes): The generated signature as a bytestring.
        Raises:
            TypeError: If the private key or random input seed is invalid.
            ValueError: If the input seed is not 32 bytes.
            TypeError: If the message is not a byte string.
        """
        c_tilde = None

        if not isinstance(private_key, (bytes, bytearray)):
            raise TypeError("Invalid private key format.")
        if not (isinstance(message, (bytes, bytearray))):
            raise TypeError("Invalid message format. Message should be in bytes")

        # line 1: breaking the private key into 6 subcomponents.
        rho, k_seed, tr, s, t0, t1 = self.encode.byte_unpack_sk(private_key)

        # modify the t1 as: -(2^d) * t1_vec, coefficient wise.
        pow_d_t1 = [[(-(1 << self.d)) * t1[i][j] for j in range(self.N)] for i in range(self.k)]

        # convert all polynomial vectors to NTT form.
        s_ntt = [self.ntt.ntt(p) for p in s]
        t0_ntt = [self.ntt.ntt(p) for p in t0]
        pow_d_t1_ntt = [self.ntt.ntt(p) for p in pow_d_t1]

        # line 2: sample a k x l matrix from input seed rho.
        matrix_a_hat = self.sample.gen_a(rho)

        # line 3: concatenating (A | I | t1_ntt) to obtain the public matrix A_prime matrix in ntt form
        id_matrix = [[[0 for _ in range(self.N)] for _ in range(self.k)] for _ in range(self.k)]
        for i in range(self.k):
            id_matrix[i][i][0] = 1
        id_ntt = [[self.ntt.ntt(p) for p in id_matrix[i]] for i in range(self.k)]

        a_prime = [matrix_a_hat[i] + id_ntt[i] + [pow_d_t1_ntt[i]] for i in range(self.k)]

        # line 4: hash the message after concatenating it after tr with shake 256 into a 64-bytes bytestring.
        mu = self.convert.hash(tr + message, 64)

        # line 6: compute a private random seed by hashing (K + input random seed + mu) with shake 256 into a 64-byte bytestring.
        rho_prime_prime = self.convert.hash(k_seed + mu, 64)
        # rho_prime_prime=self.random_bytes(64) # for randomized signing

        # initialize kappa, z and h.
        kappa = 0
        z = None
        h = None

        # line 7: rejection sampling loop.
        while z is None and h is None:

            self.total_num_of_rejections += 1  # counting average rejections

            # line 8: generate a vector of (k+l+1) polynomials using private random seed.
            y = self.sample.gen_mask(rho_prime_prime, kappa)

            # line 9: create a vector of k polynomials by multiplying A and y in NTT domain.
            y_ntt = [self.ntt.ntt(p) for p in y]
            a_prime_y = self.ntt.multiply_ntt_matrix_vector(a_prime, y_ntt)
            w = [self.ntt.inv_ntt(p) for p in a_prime_y]

            # line 10: component wise conversion to high bits.
            w_1 = [[self.operation.high_bits(w[i][j]) for j in range(self.N)] for i in range(self.k)]

            # line 11: encode the vector polynomial w_1 into a byte string and hash it after concatenating it after mu into a bytestring of size 32 using shake 256.
            c_tilde = self.convert.hash(mu + self.encode.w1_encode(w_1), 32)

            # line 12: takes an input seed rho of length 32 and converts it into a polynomial c.
            c = self.sample.sample_in_ball(c_tilde)

            c_ntt = self.ntt.ntt(c)
            cs_ntt = self.ntt.multiply_ntt_polynomial_vector(c_ntt, s_ntt)
            cs = [self.ntt.inv_ntt(p) for p in cs_ntt]

            # line 13: sampling the random bit b and constructing the response vector
            if random_bit is None:
                b = random.randint(0, 1)
            else:
                b = random_bit
            if not b:
                z = self.ntt.add_polynomial_vectors(y, cs)
            else:
                minus_cs = [[(-1) * cs[i][j] for j in range(self.N)] for i in range(self.k + self.l + 1)]
                z = self.ntt.add_polynomial_vectors(y, minus_cs)

            # line 14: check l infinity norm for z
            if self.convert.infinity_norm(z) >= self.gamma1 - self.beta:
                z = None
                h = None
            else:
                # line 15: calculating the hint vector componentwise
                ct0_ntt = self.ntt.multiply_ntt_polynomial_vector(c_ntt, t0_ntt)
                ct0 = [self.ntt.inv_ntt(p) for p in ct0_ntt]

                h = [[0] * self.N for _ in range(self.k)]  # initialize the empty hint vector.
                if not b:
                    if not self.convert.infinity_norm(ct0) >= self.gamma2:
                        w_plus_ct0 = self.ntt.add_polynomial_vectors(w, ct0)
                        for i in range(self.k):
                            for j in range(self.N):
                                h[i][j] = self.operation.make_hint(-ct0[i][j], w_plus_ct0[i][j])
                else:
                    minus_ct0 = [[(-1) * ct0[i][j] for j in range(self.N)] for i in range(self.k)]
                    if not self.convert.infinity_norm(minus_ct0) >= self.gamma2:
                        w_minus_ct0 = self.ntt.add_polynomial_vectors(w, minus_ct0)
                        for i in range(self.k):
                            for j in range(self.N):
                                h[i][j] = self.operation.make_hint(-minus_ct0[i][j], w_minus_ct0[i][j])

                if self.convert.calc_ones(h) > self.omega:
                    z = None
                    h = None

            kappa = kappa + (self.l + self.k + 1)

        # line 17: encode the signature with c_tilda, z and h.
        sigma = self.encode.sig_encode(c_tilde, self.convert.centered_modulus(z), h)

        return sigma

    def dsa_verify(self, public_key: bytes, message, signature: bytes) -> bool:
        """
        Internal function to verify a signature for a formatted message M'.
        Args:
            public_key (bytes): The public key bytestring.
            message (bytes): The message in bytes.
            signature (bytes): The signature bytestring.
        Returns:
            result (bool): True if the signature is valid, False otherwise.
        Raises:
            ValueError: If the public key or signature is invalid.
            TypeError: If the message is not a byte string.
        """
        if not isinstance(public_key, bytes):
            raise ValueError("Invalid public key format.")
        if not (isinstance(message, (bytes, bytearray))):
            raise TypeError("Invalid message format. Message should be in bytes")
        if not isinstance(signature, bytes):
            raise ValueError("Invalid signature format.")

        rho, t1 = self.encode.byte_unpack_pk(public_key)

        c_tilde, z, h = self.encode.sig_decode(signature)

        if h is None:
            return False

        a_hat = self.sample.gen_a(rho)

        pow_d_t1 = [[(-(1 << self.d)) * t1[i][j] for j in range(self.N)] for i in range(self.k)]

        pow_d_t1_ntt = [self.ntt.ntt(p) for p in pow_d_t1]

        # line 8: concatenating (A | I | t1_ntt) to obtain the public matrix A_prime matrix in ntt form
        id_matrix = [[[0 for _ in range(self.N)] for _ in range(self.k)] for _ in range(self.k)]
        for i in range(self.k):
            id_matrix[i][i][0] = 1
        id_ntt = [[self.ntt.ntt(p) for p in id_matrix[i]] for i in range(self.k)]

        a_prime = [a_hat[i] + id_ntt[i] + [pow_d_t1_ntt[i]] for i in range(self.k)]

        tr = self.convert.hash(public_key, 32)

        mu = self.convert.hash(tr + message, 64)

        # Compute: A ◦ NTT(z)
        z_ntt = [self.ntt.ntt(p) for p in z]
        a_prime_z_ntt = self.ntt.multiply_ntt_matrix_vector(a_prime, z_ntt)

        a_prime_z = [self.ntt.inv_ntt(p) for p in a_prime_z_ntt]

        # line 11 : computing the high-bits of w using the hint vector
        w1 = [[0 for _ in range(self.N)] for _ in range(self.k)]
        for i in range(self.k):
            for j in range(self.N):
                w1[i][j] = self.operation.use_hint(h[i][j], a_prime_z[i][j])

        c_hash_encoded = self.convert.hash(mu + self.encode.w1_encode(w1), 32)

        return (self.convert.infinity_norm(z) < (self.gamma1 - self.beta)) and (c_hash_encoded == c_tilde)