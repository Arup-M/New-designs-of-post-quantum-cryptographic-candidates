import random

class PolynomialRing:
    def __init__(self, q, n):
        """
            Initialize a polynomial ring with modulus {q} and degree {n-1}. I.e., {R = Z_q[x]/<x^n+1>}
            :param q: Modulus for the polynomial coefficients.
            :param n: Degree of the polynomial ring.
        """
        if not isinstance(q, int) or q <= 1:
            raise ValueError("q must be an integer greater than 1")
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer")

        self.q = q
        self.n = n
        self.element = Polynomial

    def gen(self):
        """
        Return the generator `x` of the polynomial ring
        """
        return Polynomial(self, [0,1])

    def random_element(self):
        """Generate a random polynomial in the ring."""
        coefficients = [random.randint(0, self.q - 1) for _ in range(self.n)]
        return Polynomial(self, coefficients)

    def __call__(self, coefficients):
        if isinstance(coefficients, int):
            return self.element(self, [coefficients])
        if not all(isinstance(c, int) for c in coefficients):
            raise ValueError("All coefficients must be integers.")
        if not isinstance(coefficients, list):
            raise TypeError(
                f"Polynomials should be constructed from a list of integers, of length at most d = {self.n}"
            )
        return self.element(self, coefficients)

    def __repr__(self):
        return f"Uni-variate Polynomial Ring in x over Finite Field of size {self.q} with modulus x^{self.n} + 1"



class Polynomial:
    def __init__(self, parent, coefficients_list):
        """
        Create a polynomial in a given ring.

        :param parent: The parent PolynomialRing.
        :param coefficients_list: List of coefficients (mod q). The size of the list should be less than self.ring.n
        """
        if not hasattr(parent, 'n') or not hasattr(parent, 'q'):
            raise ValueError("Ring object must have attributes 'n' and 'q'")
        if len(coefficients_list) > parent.n:
            raise ValueError(f"coefficients_list size must be less than or equal to ring.n ({parent.n})")
        if not all(isinstance(c, int) for c in coefficients_list):
            raise ValueError("All coefficients must be integers")
        if not coefficients_list:  # Empty input implies zero-polynomial
            coefficients_list = [0]

        self.parent = parent
        self.coefficients = self._parse_coefficients(coefficients_list)

    def _parse_coefficients(self, coefficients):
        """
        Helper function which right-pads with zeros to allow polynomial construction.
        Modifies coefficients to be within the range [0, ring.q].
        :param coefficients: Original list of coefficients.
        :return: A padded and reduced list of coefficients.
        """
        # Pad with zeros to match the required length
        coefficients = coefficients + [0] * (self.parent.n - len(coefficients))

        # Reduce all coefficients modulo the ring's modulus q
        #return [c % self.parent.q for c in coefficients]
        return coefficients

    def reduce_coefficients(self):
        """
        Reduce all coefficients modulo q
        """
        self.coefficients = [c % self.parent.q for c in self.coefficients]
        return self

    def _add_mod_q(self, x, y):
        """
        add two coefficients modulo q
        """
        return (x + y) % self.parent.q

    def _sub_mod_q(self, x, y):
        """
        sub two coefficients modulo q
        """
        return (x - y) % self.parent.q

    def _add_(self, other):
        if isinstance(other, type(self)):
            new_coefficients = [
                self._add_mod_q(x, y) for x, y in zip(self.coefficients, other.coefficients)
            ]
        elif isinstance(other, int):
            new_coefficients = self.coefficients.copy()
            new_coefficients[0] = self._add_mod_q(new_coefficients[0], other)
        else:
            raise NotImplementedError("Polynomials can only be added to each other")
        return new_coefficients

    def _sub_(self, other):
        if isinstance(other, type(self)):
            new_coefficients = [
                self._sub_mod_q(x, y) for x, y in zip(self.coefficients, other.coefficients)
            ]
        elif isinstance(other, int):
            new_coefficients = self.coefficients.copy()
            new_coefficients[0] = self._sub_mod_q(new_coefficients[0], other)
        else:
            raise NotImplementedError(
                "Polynomials can only be subtracted from each other"
            )
        return new_coefficients

    def __add__(self, other):
        new_coefficients = self._add_(other)
        return self.parent(new_coefficients)

    def __radd__(self, other):
        if not isinstance(other, (int, Polynomial)):  # Adjust as necessary
            return NotImplemented
        return self.__add__(other)
    
    def __iadd__(self, other):
        if not isinstance(other, (int, Polynomial)):
            raise TypeError("Can only add a Polynomial or int instance to another Polynomial instance")
        # Perform addition and update coefficients using the class's internal logic
        result = self + other
        self.coefficients = result.coefficients
        return self

    def __sub__(self, other):
        new_coefficients = self._sub_(other)
        return self.parent(new_coefficients)

    def __rsub__(self, other):
        if isinstance(other, int):
            # Subtract the polynomial from the integer (use negation of polynomial coefficients)
            neg_self = Polynomial(self.parent, [-c % self.parent.q for c in self.coefficients])
            return neg_self + other
        elif isinstance(other, Polynomial):
            raise TypeError(f"Unsupported operand type(s) for -: '{type(other)}' and '{type(self)}'")
        return NotImplemented

    def __isub__(self, other):
        if not isinstance(other, (int, Polynomial)):
            raise TypeError("Can only add a Polynomial or int instance to another Polynomial instance")
        # Perform addition and update coefficients using the class's internal logic
        result = self - other
        self.coefficients = result.coefficients
        return self

    def _schoolbook_multiplication(self, other):
        """
        Naive implementation of polynomial multiplication
        suitable for all R_q = F_1[X]/(X^n + 1)
        :param other: The other polynomial to multiply.
        :return: Resultant Polynomial after multiplication and modular reduction.
        """
        a = list(self.coefficients)
        b = list(other.coefficients)

        # Initialize result coefficients with zeros
        ab = [0] * self.parent.n

        # Perform multiplication
        for i in range(self.parent.n):
            for j in range(0, self.parent.n - i):
                ab[i + j] = (ab[i + j] +  (a[i] * b[j]) % self.parent.q) % self.parent.q
            for j in range(self.parent.n - i, self.parent.n):
                ab[i + j - self.parent.n] = (ab[i + j - self.parent.n] - (a[i] * b[j]) % self.parent.q) % self.parent.q
        return ab

    def __neg__(self):
        """
        Returns -f, by negating all coefficients
        """
        neg_coefficients = [(-x % self.parent.q) for x in self.coefficients]
        return self.parent(neg_coefficients)

    def __mul__(self, other):
        if isinstance(other, type(self)):
            new_coefficients =  self._schoolbook_multiplication(other)
        elif isinstance(other, int):
            new_coefficients = [(c * other) % self.parent.q for c in self.coefficients]
        else:
            raise NotImplementedError(
                "Polynomials can only be multiplied by each other, or scaled by integers"
            )
        return self.parent(new_coefficients)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        result = self * other
        self.coefficients = result.coefficients
        return self

    def __pow__(self, n):
        """
        Raise a polynomial to a positive integer power using the square-and-multiply algorithm.

        Args:
            n (int): The exponent must be a non-negative integer.

        Returns:
            Polynomial: The current polynomial raised to the power of n.

        Raises:
            TypeError: If n is not an integer.
            ValueError: If n is negative.
        """
        if not isinstance(n, int):
            raise TypeError(
                "Exponentiation of a polynomial must be done using an integer."
            )

        # Deal with negative scalar multiplication
        if n < 0:
            raise ValueError(
                "Negative powers are not supported for elements of a Polynomial Ring"
            )
        # Initialize result as the identity polynomial
        f = self
        g = self.parent(1) # Assuming this is the identity polynomial

        # Edge case: n == 0 should return the identity element
        if n == 0:
            return g

        # Square-and-multiply algorithm
        while n > 0:
            if n % 2 == 1:
                g = g * f  # Multiply result by base
            f = f * f  # Square the base
            n //= 2  # Divide exponent by 2
        return g

    def is_constant(self):
        """
        Check if the polynomial is a constant.

        :return: True if the polynomial has only one non-zero term.
        """
        return all(c == 0 for c in self.coefficients[1:])

    def is_zero(self):
        """
        Return if polynomial is zero: f = 0
        """
        return all(c == 0 for c in self.coefficients)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.coefficients == other.coefficients
        elif isinstance(other, int):
            if self.is_constant() and (other % self.parent.q) == self.coefficients[0]:
                return True
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __req__(self, other):
        """
        Check if an integer is equal to the polynomial (when the polynomial is on the right-hand side).
        :param other: The integer to compare.
        :return: True if other equals this polynomial, False otherwise.
        """
        return self.__eq__(other)

    def __repr__(self):
        if self.is_zero():
            return "0"

        terms = []
        for i, c in enumerate(self.coefficients):
            if c != 0:
                if i == 0:
                    terms.append(f"{c}")
                elif i == 1:
                    terms.append(f"{c}*x" if c != 1 else "x")
                else:
                    terms.append(f"{c}*x^{i}" if c != 1 else f"x^{i}")

        # Handle signs and join terms
        output = terms[0]
        for term in terms[1:]:
            if not term.startswith("-"):
                output += " + "
            output += term
        return f"{self.__class__.__name__}({output})"

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, index):
        """
            Returns the coefficient at the specified index in the coefficients_list.
            This method provides access to the elements contained in the sequence of coefficients.

            Parameters:
                index (int): The position in the list of coefficients whose value needs to be retrieved.

            Returns:
                int: The coefficient present at the specified position in the list.
        """
        return self.coefficients[index]

