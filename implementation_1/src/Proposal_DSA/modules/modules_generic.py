class Module:
    def __init__(self, ring):
        """
        Initialize a module over the ring ``ring``
        :param ring: a commutative ring object
        """
        self.ring = ring
        self.matrix = Matrix

    def random_element(self, m, n):
        """
        Generate a random element of the module of dimension m x n
        """
        elements = [[self.ring.random_element() for _ in range(n)] for _ in range(m)]
        return self(elements)

    def __repr__(self):
        return f"Module over the commutative ring: {self.ring}"

    def __str__(self):
        return f"Module over the commutative ring: {self.ring}"

    def __call__(self, matrix_elements, transpose=False):
        if not isinstance(matrix_elements, list):
            raise TypeError(
                "elements of a module are matrices, built from elements of the base ring"
            )

        if isinstance(matrix_elements[0], list):
            for element_list in matrix_elements:
                if not all(isinstance(aij, self.ring.element) for aij in element_list):
                    raise TypeError(
                        f"All elements of the matrix must be elements of the ring: {self.ring}"
                    )
            return self.matrix(self, matrix_elements, transpose=transpose)

        elif isinstance(matrix_elements[0], self.ring.element):
            if not all(isinstance(aij, self.ring.element) for aij in matrix_elements):
                raise TypeError(
                    f"All elements of the matrix must be elements of the ring: {self.ring}"
                )
            return self.matrix(self, [matrix_elements], transpose=transpose)

        else:
            raise TypeError(
                "elements of a module are matrices, built from elements of the base ring"
            )
    def vector(self, list_of_element):
        """
        Construct a column vector (note transpose ={True}) given a list of elements of the module's ring

        :param list_of_element: a list of elements of the ring
        :return: a vector of the module
        """
        return self.matrix(self, [list_of_element], transpose=True)

class Matrix:
    def __init__(self, parent, matrix_data, transpose=False):
        self.parent = parent
        self.data = matrix_data
        self._transpose = transpose
        if not self._check_dimensions():
            raise ValueError("Inconsistent row lengths in matrix")

    def _check_dimensions(self):
        """
        Ensure that the matrix is rectangular
        """
        # Validate that self.data is a non-empty 2D list
        if not isinstance(self.data, list) or not all(isinstance(row, list) for row in self.data):
            raise TypeError("Matrix must be a list of lists")

        # Allow empty matrices
        if not self.data:
            return True

        # Check if all rows have the same length
        first_row_length = len(self.data[0])
        return all(len(row) == first_row_length for row in self.data)

    def dim(self):
        """
        Return the dimensions of the matrix with m rows
        and n columns

        :return: the dimension of the matrix ``(m, n)``
        :rtype: tuple(int, int)
        """
        if not self._transpose:
            return len(self.data), len(self.data[0])
        else:
            return len(self.data[0]), len(self.data)

    def transpose(self):
        """
        Return a matrix with the rows and columns of swapped
        """
        return self.parent(self.data, not self._transpose)

    def transpose_self(self):
        """
        Swap the rows and columns of the matrix in place
        """
        self._transpose = not self._transpose
        return

    #T = property(transpose)  # Define clearly as a class field with a descriptive name: still unclear

    def reduce_coefficients(self):
        """
        Reduce every element in the polynomial
        using the modulus of the PolynomialRing
        """
        for row in self.data:
            for poly in row:
                if not hasattr(poly, "reduce_coefficients"):
                    raise AttributeError(f"Element {poly} does not have a 'reduce_coefficients' method.")

                try:
                    poly.reduce_coefficients()
                except Exception as e:
                    raise RuntimeError(f"Failed to reduce coefficients for element {poly}: {e}")
        return self

    def __getitem__(self, idx):
        """
        Retrieve the element at row i and column j of the matrix.

        Parameters:
            idx (tuple): A tuple (i, j) where i is the row index (0-based) and j is the column index (0-based).

        Returns:
            The value at row i and column j of the (possibly transposed) matrix.

        Raises:
            AssertionError: If idx is not a tuple of length 2.
            IndexError: If i or j are out of bounds.
        """
        assert isinstance(idx, tuple) and len(idx) == 2, "Can't access individual rows"

        # Validate that data is correctly structured
        if not self.data:
            raise IndexError("Cannot access elements of an empty matrix.")

        if not (0 <= idx[0] < self.dim()[0] and 0 <= idx[1] < self.dim()[1]):
            raise IndexError(f"Index out of bounds: {idx} (0-based indexing)")

        if not self._transpose:
            return self.data[idx[0]][idx[1]]
        else:
            return self.data[idx[1]][idx[0]]

    def __eq__(self, other):
        """
        Determines if two objects are equal based on their dimensions and element-wise
        equality.

        Parameters
        ----------
        other : Any
            The object to compare with the current instance.

        Returns
        -------
        bool
            True if the dimensions match and all corresponding elements are equal,
            False otherwise.
        """
        if not isinstance(other, Matrix):  # Ensure `other` is the correct type
            return False

        if self.dim() != other.dim():  # Compare dimensions
            return False

        m, n = self.dim()

        if m == 0 and n == 0:  # Handle empty matrices
            return True

        return all([self[i, j] == other[i, j] for i in range(m) for j in range(n)])


    def __neg__(self):
        """
            Returns {-self}, by negating all elements
        """
        if not self.data:  # Check if the matrix is empty
            return self.parent([], self._transpose)

        m, n = self.dim()
        return self.parent(
            [[-self[i, j] for j in range(n)] for i in range(m)],
            self._transpose,
        )

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can only add matrices to other matrices from the same class hierarchy")
        if self.parent != other.parent:
            raise TypeError("Matrices must have the same base ring")
        if self.dim() != other.dim():
            raise ValueError("Matrices are not of the same dimensions")

        m, n = self.dim()
        if m == 0 or n == 0:
            return self.parent([], False)

        # Perform matrix addition element-wise
        result_data = [
            [self[i, j] + other[i, j] for j in range(n)]
            for i in range(m)
        ]

        # Return the resulting matrix
        return self.parent(result_data, False)

    def __iadd__(self, other):
        if self.dim() != other.dim():
            raise ValueError("Matrices are not of the same dimensions")
        m, n = self.dim()
        # Perform in-place addition
        for i in range(m):
            for j in range(n):
                self.data[i][j] += other[i, j]
        return self

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can only subtract matrices to other matrices from the same class hierarchy")
        if self.parent != other.parent:
            raise TypeError("Matrices must have the same base ring")
        if self.dim() != other.dim():
            raise ValueError("Matrices are not of the same dimensions")

        m, n = self.dim()
        return self.parent(
            [[self[i, j] - other[i, j] for j in range(n)] for i in range(m)],
            False,
        )

    def __isub__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError("Can only add matrices to other matrices")
        if self.parent != other.parent:
            raise TypeError("Matrices must have the same base ring")
        if self.dim() != other.dim():
            raise ValueError("Matrices are not of the same dimensions")

        m, n = self.dim()
        # Perform in-place subtraction
        for i in range(m):
            for j in range(n):
                self.data[i][j] -= other[i, j]
        return self

    def __matmul__(self, other):
        """
        Denoted A @ B
        """
        if not isinstance(other, type(self)):
            raise TypeError("Can only multiply matrices with other matrices")
        if self.parent != other.parent:
            raise TypeError("Matrices must have the same base ring")

        m, n = self.dim()
        n_, l = other.dim()
        if not n == n_:
            raise ValueError("Matrices are of incompatible dimensions")

        return self.parent(
            [
                [sum(self[i, k] * other[k, j] for k in range(n)) for j in range(l)]
                for i in range(m)
            ]
        )

    def scale(self, other):
        """
        Multiply each element of the matrix by a polynomial or integer
        """
        if not (isinstance(other, self.parent.ring.element) or isinstance(other, int)):
            raise TypeError("Can only multiply elements with polynomials or integers")

        result_data = [[other * poly for poly in row] for row in self.data]
        return result_data, self.parent(result_data, transpose=self._transpose) #TODO: fix it

    def dot(self, other): ## To make it better
        """
        Compute the inner product of two vectors
        """
        if not isinstance(other, type(self)):
            raise TypeError("Can only perform dot product with other matrices")
        m, n = self.dim()
        m_, n_ = other.dim()
        if not m == m_ or not n == 1 or not n_ == 1:
            raise ValueError("Matrices are of incompatible dimensions")

        res = self.transpose() @ other
        assert res.dim() == (1, 1), "Matrix dimensions do not match. Expected (1, 1), got:"
        return res[0, 0]


    def __repr__(self):
        m, n = self.dim()

        if m == 1:
            return str(self.data[0])

        max_col_width = [max(len(str(self[i, j])) for i in range(m)) for j in range(n)]
        info = "]\n[".join(
            [
                ", ".join([f"{str(self[i, j]):>{max_col_width[j]}}" for j in range(n)])
                for i in range(m)
            ]
        )
        return f"[{info}]"