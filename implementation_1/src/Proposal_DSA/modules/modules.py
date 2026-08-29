from ..modules.modules_generic import Module, Matrix
from ..polynomials.polynomials import PolynomialRingDSA
import math

class ModuleDSA(Module):
    def __init__(self,q,n,root_of_unity):
        # Initialize the parent class (if needed)
        super().__init__(PolynomialRingDSA(q, n, root_of_unity))
        self.matrix = MatrixDSA

    def __bit_unpack(self, input_bytes, no_rows, no_columns, algorithm, n_bits, n_bytes): # nBytes: number of bytes per polynomial
        assert len(input_bytes) == no_rows * no_columns * n_bytes, "Input bytes length is incorrect"
        poly_bytes = [
            input_bytes[i: i + n_bytes]
            for i in range(0, len(input_bytes), n_bytes) # split input_bytes into n_bytes chunks
        ]
        mat = [
            [algorithm(poly_bytes[no_columns  * i + j], n_bits) for j in range(no_columns)] for i in range(no_rows)
        ]
        return self(mat)

    def bit_unpack_t0(self, input_bytes, no_rows, no_columns, n_bits):
        n_bytes = math.ceil(self.ring.n * n_bits / 8)
        algorithm = self.ring.bit_unpack_t0
        return self.__bit_unpack(input_bytes, no_rows, no_columns, algorithm, n_bits, n_bytes)

    def bit_unpack_t1(self, input_bytes, no_rows, no_columns, n_bits):
        #n_bytes = 320
        n_bytes = math.ceil(self.ring.n * n_bits / 8)
        algorithm = self.ring.bit_unpack_t1
        return self.__bit_unpack(input_bytes, no_rows, no_columns, algorithm, n_bits, n_bytes)

    def bit_unpack_s(self, input_bytes, no_rows, no_columns, eta): # TODO: Singh: crosscheck it once more
        algorithm = self.ring.bit_unpack_s
        n_bits_eta = math.ceil(math.log(2*eta + 1, 2))
        n_bytes = math.ceil(self.ring.n * n_bits_eta / 8)
        return self.__bit_unpack(input_bytes, no_rows, no_columns, algorithm, n_bits_eta, n_bytes)

    def bit_unpack_w(self, input_bytes, no_rows, no_columns, gamma_2): #TODO: change to bit_unpack_w1
        n_bits_gamma_2 = math.ceil(math.log((self.ring.q - 1) / (2 * gamma_2) - 1, 2)) #TODO:Singh
        n_bytes = math.ceil(self.ring.n * n_bits_gamma_2 / 8) # = 192 TODO:
        algorithm = self.ring.bit_unpack_w
        return self.__bit_unpack(input_bytes, no_rows, no_columns, algorithm, n_bits_gamma_2, n_bytes)

    def bit_unpack_z(self, input_bytes, no_rows, no_columns, gamma_1):
        if gamma_1 == (1 << 17):
            n_bits_gamma_1 = 18
            n_bytes = 576
            algorithm = self.ring.bit_unpack_z
            return self.__bit_unpack(input_bytes, no_rows, no_columns, algorithm, n_bits_gamma_1, n_bytes)
        # Level 3 and 5 parameter set
        elif gamma_1 == (1 << 19):
            n_bits_gamma_1 = 20
            n_bytes = 640
            algorithm = self.ring.bit_unpack_z
            return self.__bit_unpack(input_bytes, no_rows, no_columns, algorithm, n_bits_gamma_1, n_bytes)
        else:
            raise ValueError("Expected gamma_1 to be either 2^17 or 2^19")



class MatrixDSA(Matrix):
    def __init__(self, parent, matrix_data, transpose=False):
        if not isinstance(matrix_data, (list, tuple)):
            raise ValueError("matrix_data must be a list or tuple")
        super().__init__(parent, matrix_data, transpose=transpose)

    def check_norm_bound(self, bound):
        """

        """
        return any(poly.check_norm_bound(bound) for row in self.data for poly in row)

    def power_2_round(self, d):
        """
        Applies `power_2_round` on every element in the
        Matrix to create two matrices.
        """
        m, n = self.dim()

        m1_elements = [[0 for _ in range(n)] for _ in range(m)]
        m0_elements = [[0 for _ in range(n)] for _ in range(m)]

        for i in range(m):
            for j in range(n):
                m1_ele, m0_ele = self[i, j].power_2_round(d)
                m1_elements[i][j] = m1_ele
                m0_elements[i][j] = m0_ele

        return self.parent(m1_elements, transpose=self._transpose), self.parent(
            m0_elements, transpose=self._transpose
        )

    def decompose(self, alpha):
        """
        Applies `power_2_round` on every element in the
        Matrix to create two matrices.
        """
        m, n = self.dim()

        m1_elements = [[0 for _ in range(n)] for _ in range(m)]
        m0_elements = [[0 for _ in range(n)] for _ in range(m)]

        for i in range(m):
            for j in range(n):
                m1_ele, m0_ele = self[i, j].decompose(alpha)
                m1_elements[i][j] = m1_ele
                m0_elements[i][j] = m0_ele

        return self.parent(m1_elements, transpose=self._transpose), self.parent(
            m0_elements, transpose=self._transpose
        )


    def to_ntt(self):
        """
        Convert every element of the matrix into NTT form
        """
        data = [[poly.to_ntt() for poly in row] for row in self.data]
        return self.parent(data, transpose=self._transpose)

    def from_ntt(self):
        """
        Convert every element of the matrix from NTT form
        """
        data = [[x.from_ntt() for x in row] for row in self.data]
        return self.parent(data, transpose=self._transpose)


    def high_bits(self, alpha, is_ntt=False):
        matrix = [
            [ele.high_bits(alpha, is_ntt=is_ntt) for ele in row] for row in self.data
        ]
        return self.parent(matrix)

    def low_bits(self, alpha, is_ntt=False):
        matrix = [
            [ele.low_bits(alpha, is_ntt=is_ntt) for ele in row] for row in self.data
        ]
        return self.parent(matrix)

    def make_hint(self, other, alpha):
        matrix = [
            [p.make_hint(q, alpha) for p, q in zip(r1, r2)]
            for r1, r2 in zip(self.data, other.data)
        ]
        return self.parent(matrix)

    def use_hint(self, other, alpha):
        matrix = [
            [p.use_hint(q, alpha) for p, q in zip(r1, r2)]
            for r1, r2 in zip(self.data, other.data)
        ]
        return self.parent(matrix)

    def sum_hint(self):
        """
            Helper functions to count the number of coefficients that are equal to 1
            in all the polynomials of a matrix
        """
        return sum(c for row in self.data for p in row for c in p)

    ######################################################################
    #  Bit packing matrix data
    ######################################################################

    def __bit_pack(self, algorithm, n_bits):
        return b"".join(algorithm(poly, n_bits) for row in self.data for poly in row)

    def bit_pack_t1(self, n_bits):
        algorithm = self.parent.ring.element.bit_pack_t1
        return self.__bit_pack(algorithm, n_bits)

    def bit_pack_t0(self, n_bits):
        algorithm = self.parent.ring.element.bit_pack_t0
        return self.__bit_pack(algorithm, n_bits)

    def bit_pack_s(self, eta): #TODO: Fix it
        n_bits_eta = math.ceil(math.log(2*eta + 1, 2))
        algorithm = self.parent.ring.element.bit_pack_s
        return self.__bit_pack(algorithm, n_bits_eta)

    def bit_pack_w(self, gamma_2):
        n_bits_gamma_2 = math.ceil(math.log((self.parent.ring.q - 1) / (2 * gamma_2) - 1, 2))
        algorithm = self.parent.ring.element.bit_pack_w
        return self.__bit_pack(algorithm, n_bits_gamma_2)


    def bit_pack_z(self, gamma_1):
        if gamma_1 == (1 << 17):
            n_bits_gamma_1 = 18
            algorithm = self.parent.ring.element.bit_pack_z
            return self.__bit_pack(algorithm, n_bits_gamma_1)
        else:
            if gamma_1 == (1 << 19):
                n_bits_gamma_1 = 20
                algorithm = self.parent.ring.element.bit_pack_z
                return self.__bit_pack(algorithm, n_bits_gamma_1)
            else:
                raise ValueError("gamma_1 must be either 2^17 or 2^19")



