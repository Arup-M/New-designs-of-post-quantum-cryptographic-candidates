from .conversion import Conversion


class NTT:
    def __init__(self, n, q, d):
        # self.N = 256 # fixed for all
        # self.q = 8383489 # fixed for all
        # self.d = 13 # fixed for all

        self.N = n
        self.q = q
        self.d = d

        self.convert = Conversion(q, n)

        if self.q == 8380417:
            self.ZETAS = [
                0, 4808194, 3765607, 3761513, 5178923, 5496691, 5234739, 5178987,
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

    # def bit_rev(self, m:bytes) -> bytes:
    #     b = self.convert.integer_to_bits(m,8)
    #     b_rev=[0]*8
    #     for i in range (8):
    #         b_rev[i] = b[7-i]
    #     r=self.convert.bits_to_integer(b_rev,8)
    #     return r

    # def zeta(self):
    #     root_of_unity=11998
    #     zetas=[0]*(self.N)
    #     for i in range (self.N):
    #         if i == 0:
    #             zetas[i]=0
    #         else:
    #             zetas[i]=pow(root_of_unity,self.bit_rev(i)) % (self.q)
    #     return zetas

    def ntt(self, coefficient_list) -> list:
        """
        Algorithm 41 FIPS 204

        Computes the ntt of a polynomial.
        Args:
            coefficient_list (list): list of integers representing polynomial coefficients.
        Returns:
            w_hat (list): list of integers representing NTT transformed polynomial coefficients.
        Raises:
            TypeError: If the input is not a list or tuple, or if any coefficient is not an integer.
            ValueError: If the input list does not contain exactly 256 elements.
        """

        # --- Input checks ---
        if not isinstance(coefficient_list, (list, tuple)):
            raise TypeError(f"Expected a list or tuple, got {type(coefficient_list).__name__}")

        if len(coefficient_list) != self.N:
            raise ValueError(f"Expected 256 elements, got {len(coefficient_list)}")

        if not all(isinstance(x, (int, float)) for x in coefficient_list):
            raise TypeError("All coefficients of the polynomial must be integers.")

        # ZETAS =self.zeta()

        # line 1 to 5: initialize w_hat, m and len.
        w_hat = [coefficient_list[i] for i in range(self.N)]  # make a copy of the input so that it remains unchanged.
        m = 0
        length = 128

        # line 6 to 8: start 2 loops and initialize 'start'.
        while length >= 1:
            start = 0
            while start < self.N:

                # line 9: increment m.
                m = m + 1

                # line 10: assign zetas value to z where zetas are precomputed.
                z = self.ZETAS[m]

                # line 11 to 15: butterfly operation.
                for j in range(start, start + length):
                    t = (z * w_hat[j + length]) % self.q
                    w_hat[j + length] = (w_hat[j] - t) % self.q
                    w_hat[j] = (w_hat[j] + t) % self.q

                # line 16: increment 'start' by left shifted 'length'.
                start = start + 2 * length

            # line 18: update length. ( 128 -> 64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1 )
            length >>= 1

        # line 20: return w_hat
        return w_hat

    def multiply_ntt(self, vec_a: list, vec_b: list) -> list:
        """
        Computes ntt product of two polynomials in NTT domain.
        Args:
            vec_a (list): list of integers representing polynomial coefficients in ntt domain.
            vec_b (list): list of integers representing polynomial coefficients in ntt domain.
        Returns:
            c (list): list of integers representing NTT multiplied polynomial coefficients.
        Raises:
            TypeError: If the inputs are not lists or tuples.
            ValueError: If the input lists are not of equal size.
        """
        if not isinstance(vec_a, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vec_a, got {type(vec_a)}")
        if not isinstance(vec_b, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vec_b, got {type(vec_b)}")
        if len(vec_a) != len(vec_b):
            raise ValueError(f"both lists must be of equal size to perform NTT multiplication.")

        c = [0 for _ in range(self.N)]

        for i in range(self.N):
            c[i] = (vec_a[i] * vec_b[i]) % self.q

        return c

    def multiply_ntt_matrix_vector(self, matrix: list, vector: list) -> list:
        """
        Multiplies a matrix of polynomials with a vector of polynomials in NTT domain.
        Args:
            matrix (list): A matrix of polynomials (list of lists of ints) in NTT domain.
            vector (list): A vector of polynomials (list of ints) in NTT domain.
        Returns:
            result (list): The resulting vector of polynomials after multiplication in NTT domain.
        Raises:
            TypeError: If the inputs are not lists or tuples.
            ValueError: If the dimensions of the matrix and vector are incompatible.
        """
        if not isinstance(matrix, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for matrix, got {type(matrix)}")
        if not isinstance(vector, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vector, got {type(vector)}")
        if len(matrix) == 0 or len(matrix[0]) != len(vector):
            raise ValueError("Incompatible dimensions for matrix-vector multiplication.")

        result = [[0] * self.N for _ in range(len(matrix))]  # initialize product of A_cap and NTT(s1)
        for i in range(len(matrix)):
            for j in range(len(vector)):
                element_product = self.multiply_ntt(matrix[i][j], vector[j])
                result[i] = self.add_ntt(result[i], element_product)

        return result

    def multiply_ntt_polynomial_vector(self, poly: list, vector: list) -> list:
        """
        Multiplies a polynomial with a vector of polynomials in NTT domain.
        Args:
            poly (list): A polynomial (list of ints) in NTT domain.
            vector (list): A vector of polynomials (list of lists of ints) in NTT domain.
        Returns:
            result (list): The resulting vector of polynomials after multiplication in NTT domain.
        Raises:
            TypeError: If the inputs are not lists or tuples.
            ValueError: If the dimensions of the polynomial and vector are incompatible.
        """
        if not isinstance(poly, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for poly, got {type(poly)}")
        if not isinstance(vector, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vector, got {type(vector)}")
        if len(vector) == 0 or len(vector[0]) != len(poly):
            raise ValueError("Incompatible dimensions for polynomial-vector multiplication.")

        result = [[0] * self.N for _ in range(len(vector))]  # initialize product of poly and vector
        for j in range(len(vector)):
            element_product = self.multiply_ntt(poly, vector[j])
            for i in range(self.N):
                result[j][i] = element_product[i] % self.q

        return result

    def add_ntt(self, a_vec: list, b_vec: list) -> list:
        """
        Algorithm 44 FIPS 204
        performs addition in ntt domain.
        Args:
            a_vec (list): first polynomial in ntt domain.
            b_vec (list): second polynomial in ntt domain.
        Returns:
            c (list): resulting polynomial in ntt domain after addition.
        Raises:
            TypeError: If the inputs are not lists or tuples.
            ValueError: If the input lists are not of equal size.
        """
        if not isinstance(a_vec, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for a_vec, got {type(a_vec)}")
        if not isinstance(b_vec, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for b_vec, got {type(b_vec)}")
        if len(a_vec) != len(b_vec):
            raise ValueError(f"both lists must be of equal size to perform NTT multiplication.")

        c = [0 for _ in range(self.N)]

        for i in range(self.N):
            c[i] = (a_vec[i] + b_vec[i]) % self.q

        return c

    def add_vector_ntt(self, vector1: list, vector2: list) -> list:
        """
        Adds two vectors of polynomials in NTT domain component-wise.
        Args:
            vector1 (list): First vector of polynomials (list of lists of ints) in NTT domain.
            vector2 (list): Second vector of polynomials (list of lists of ints) in NTT domain.
        Returns:
            result (list): The resulting vector of polynomials after addition in NTT domain.
        Raises:
            TypeError: If the inputs are not lists or tuples.
        """
        if not isinstance(vector1, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vector1, got {type(vector1)}")
        if not isinstance(vector2, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vector2, got {type(vector2)}")
        if not len(vector1) == len(vector2):
            raise ValueError("Both vectors must have the same length for addition.")

        result = [[0] * self.N for _ in range(len(vector1))]  # initialize result vector
        for i in range(len(vector1)):
            result[i] = self.add_ntt(vector1[i], vector2[i])

        return result

    def add_polynomials(self, poly1: list, poly2: list) -> list:
        """
        Adds two polynomials coefficient-wise.
        Args:
            poly1 (list): First polynomial (list of ints).
            poly2 (list): Second polynomial (list of ints).
        Returns:
            result (list): The resulting polynomial after addition.
        Raises:
            TypeError: If the inputs are not lists or tuples.
        """
        if not isinstance(poly1, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for poly1, got {type(poly1)}")
        if not isinstance(poly2, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for poly2, got {type(poly2)}")
        if not len(poly1) == len(poly2):
            raise ValueError("Both polynomials must have the same length for addition.")

        result = [0] * len(poly1)  # initialize result polynomial
        for i in range(len(poly1)):
            result[i] = (poly1[i] + poly2[i]) % self.q

        return result

    def add_polynomial_vectors(self, vec1: list, vec2: list) -> list:
        """
        Adds two vectors of polynomials coefficient-wise.
        Args:
            vec1 (list): First vector of polynomials (list of lists of ints).
            vec2 (list): Second vector of polynomials (list of lists of ints).
        Returns:

            result (list): The resulting vector of polynomials after addition.
        Raises:
            TypeError: If the inputs are not lists or tuples.
        """
        if not isinstance(vec1, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vec1, got {type(vec1)}")
        if not isinstance(vec2, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for vec2, got {type(vec2)}")
        if not len(vec1) == len(vec2):
            raise ValueError("Both vectors must have the same length for addition.")

        result = [[0] * self.N for _ in range(len(vec1))]  # initialize result vector
        for i in range(len(vec1)):
            result[i] = self.add_polynomials(vec1[i], vec2[i])
        return result

    def sub_ntt(self, a_vec: list, b_vec: list) -> list:
        """
        performs subtraction in ntt domain.
        Args:
            a_vec (list): first polynomial in ntt domain.
            b_vec (list): second polynomial in ntt domain.
        Returns:
            c (list): resulting polynomial in ntt domain after subtraction.
        """
        if len(a_vec) != len(b_vec):
            raise ValueError(f"both lists must be of equal size to perform NTT multiplication.")

        c = [0 for _ in range(self.N)]

        for i in range(self.N):
            c[i] = (a_vec[i] - b_vec[i]) % self.q

        return c

    def inv_ntt(self, coefficient_list: list) -> list:
        """
        Algorithm 42 FIPS 204

        Computes the inverse ntt of a polynomial vector.
        Args:
            coefficient_list (list): list of integers representing polynomial coefficients in ntt domain.
        Returns:
            w (list): list of integers representing polynomial coefficients.
        Raises:
            TypeError: If the input is not a list or tuple, or if any coefficient is not an integer.
            ValueError: If the input list does not contain exactly 256 elements.
        """
        # input checks
        if not isinstance(coefficient_list, (list, tuple)):
            raise TypeError(f"Expected a list or tuple, got {type(coefficient_list).__name__}")
        if not all(isinstance(x, (int, float)) for x in coefficient_list):
            raise TypeError("All coefficients of the polynomial must be integers.")
        if len(coefficient_list) != self.N:
            raise ValueError(f"Input list must have exactly {self.N} coefficients.")

        # ZETAS =self.zeta()

        w_hat = [coefficient_list[i] for i in range(self.N)]  # make a copy of the input so that it remains unchanged.
        m = 256
        length = 1

        while length < 256:
            start = 0
            while start < 256:
                m = m - 1
                z = (-1 * self.ZETAS[m])
                for j in range(start, start + length):
                    t = w_hat[j]
                    w_hat[j] = (t + w_hat[j + length]) % self.q
                    w_hat[j + length] = (t - w_hat[j + length]) % self.q
                    w_hat[j + length] = (z * w_hat[j + length]) % self.q

                start = start + 2 * length

            length = 2 * length

        if self.q == 8380417:
            f = 8347681  # modular inverse of 256 in Zq
        else:
            f = 8350741  # modular inverse of 256 in Zq
        for j in range(self.N):
            w_hat[j] = (w_hat[j] * f) % self.q

        return w_hat

    def power2round(self, r: int) -> tuple[int, int]:
        """
        Decomposes an integer r into high bits (r₁) and low bits (r₀).
        Args:
            r (int): An integer coefficient.
        Returns:
            tuple (r₁, r₀): A tuple containing the high bits r₁ and low bits r₀.
        """
        # 1: r⁺ ← r mod q
        r_plus = r % self.q

        # 2: r₀ ← r⁺ mod± 2ᵈ
        mod_val = 2 ** self.d
        r0 = r_plus % mod_val

        # Adjust to the centered range [-2^(d-1)+1, 2^(d-1)]
        if r0 > mod_val // 2:
            r0 -= mod_val

        # 3: return ((r⁺ - r₀)/2ᵈ, r₀)
        r1 = (r_plus - r0) // mod_val

        return r1, r0

    def power2round_vec(self, t_vec: list) -> tuple[list, list]:
        """
        Applies Power2Round component-wise to a vector of polynomials.
        Args:
            t_vec (list): A vector of polynomials (list of lists of ints).
        Returns:
            tuple (t₁, t₀): Two vectors of polynomials, where t₁ contains the high bits and t₀ contains the low bits.
        Raises:
            TypeError: If the input is not a list or tuple, or if any polynomial or coefficient is not an integer.
        """
        if not isinstance(t_vec, (list, tuple)):
            raise TypeError(f"Expected a list or tuple for t_vec, got {type(t_vec)}")
        for poly in t_vec:
            if not isinstance(poly, (list, tuple)):
                raise TypeError(f"Expected a list or tuple for polynomial, got {type(poly)}")
            for coeff in poly:
                if not isinstance(coeff, (int, float)):
                    raise TypeError("All coefficients of the polynomial must be integers.")

        t1_vec = []
        t0_vec = []

        for poly in t_vec:
            # print(poly)
            poly_t1 = []
            poly_t0 = []
            for coeff in poly:
                r1, r0 = self.power2round(coeff)
                poly_t1.append(r1)
                poly_t0.append(r0)
            t1_vec.append(poly_t1)
            t0_vec.append(poly_t0)

        return t1_vec, t0_vec
