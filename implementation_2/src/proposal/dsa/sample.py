import hashlib
import math

#from typing import Optional
from .conversion import Conversion
from .packing import Packing

class Sample:
    def __init__(self, q, n, eta, gamma1, k, l, tau, omega):
        # self.N = 256 # fixed for all 
        # self.q = 8383489 # fixed for all

        self.q = q
        self.N = n
        
        self.eta = eta
        self.gamma1 = gamma1
        self.l = l
        self.k = k
        self.tau = tau
        self.omega = omega

        self.convert = Conversion(self.q, self.N)
        self.packing = Packing(self.q, self.N, self.omega, self.k)

    def coeff_from_three_bytes(self, b0: int, b1: int, b2:int) :
        """
        generates a number z from three input bytes b0, b1, b2.
        
        such that z belongs to {0, 1, 2, ... , q - 1} U { None }
        Args:
            b0 (int): first byte (0 - 255). 
            b1 (int): second byte (0 - 255).
            b2 (int): third byte (0 - 255).
        Returns:
            z (int): sampled coefficient or 'None' if rejected.
        Raises:
            TypeError: if any of b0, b1, b2 is not an integer
        """
        # checks for validity of inputs.
        for i, b in enumerate((b0, b1, b2), start = 0):
            if not isinstance(b, int):
                raise TypeError (f"b{i} must be in an integer.")
            if not (0 <= b <= 255):
                raise ValueError (f"b{i} must be in the range 0 - 255.")
        
        # line 1: make a copy of b2.
        b2_prime = b2

        # line 2 to 4: making sure b2_prime is 7 bits, not 8.
        if b2_prime > 127:
            b2_prime = b2_prime - 128
        
        # line 5: evaluate z for sampling.
        z = (b2_prime << 16) + (b1 << 8) + b0
        
        # line 6 to 8: reject the sample z if it's greater than q. 
        if z < self.q:
            return z # accept sample
        else:
            return None # reject sample

    def rej_ntt_poly(self, rho: bytes) -> list:
        """
        samples a polynomial from a bytestring of length 34.
        Args:
            rho (bytes): a bytestring of length 34.
        Returns:
            polynomial (list): a list of integers representing the polynomial.
        raises:
            TypeError: if rho is not a bytestring.
            ValueError: if length of rho is not 34 bytes.    
        """
        # input checks.
        if not isinstance (rho, (bytes, bytearray)):
            raise TypeError ("expected a bytestring as input.")
        if not (len(rho) == 34):
            raise ValueError ("length of rho must be exactly 34 bytes.")

        # line 1: initialize j = 0 and the polynomial with all 0 coefficients.
        j = 0
        polynomial = [0 for _ in range (self.N)]

        # line 2: initialize shake_128 ; G.init().
        ctx = hashlib.shake_128() 

        # line 3: hash rho with the shake_128 object ; # G.Absorb(ctx, rho).
        ctx.update(rho)

        byte_stream = ctx.digest(894) # store the hash in byte_stream for faster calling.
        byte_position = 0 # temporary variable to keep track of position in byte_stream.
        
        # line 4: main rejection loop.
        while j < 256:
            if byte_position + 3 > len(byte_stream): # to prevent byte_stream from going out of index.
                byte_stream += ctx.digest(self.N)
                print("ran out of bytes in rejection sampling! - max 894 bytes allowed")

            # line 5: take out next 3 bytes form the hash ; G.squeeze(ctx, 3).
            selected_3_bytes = byte_stream[byte_position : byte_position + 3]
            byte_position +=3 # update byte position to get next 3 byte on next selection.

            # line 6: sample an integer from 3 selected bytes.
            polynomial[j] = self.coeff_from_three_bytes(selected_3_bytes[0], selected_3_bytes[1], selected_3_bytes[2])
            
            # line 7 to 9: increment j if sample is accepted.
            if polynomial[j] is not None:
                j = j + 1 # sample accepted.

        # line 11: return the constructed polynomial.
        return polynomial

    def gen_a (self, rho: bytes) -> list:
        """
        samples a k x l matrix of polynomials.
        Args:
            rho (bytes): a bytestring of length 32.
        Returns:
            A (Matrix): a k x l matrix of polynomials.
        raises:
            ValueError: if length of rho is not 32 bytes.
        """
        #input checks.
        if not (len(rho) == 32) and not isinstance(rho, bytes):
            raise ValueError ("rho must be a 32-bytes bytestring.")
        
        matrix_a = [[[0 for _ in range (self.N)] for _ in range(self.l)] for _ in range(self.k)] # initialize the matrix of polynomials with all 0s.

        # line 1 to 2: loop over k and then l. 
        for r in range(self.k):
            for s in range (self.l):
                # line 3: concatenate rho with s and r.
                rho_prime = rho + self.convert.integer_to_bytes(s, 1) + self.convert.integer_to_bytes(r, 1)

                # line 4: construct a polynomial from rho_prime.
                matrix_a[r][s] = self.rej_ntt_poly(rho_prime)
        
        return matrix_a # return the matrix A.
    
    def coeff_from_half_byte(self, b: int):
        """
        generates an element of {-eta, -eta+1, ... , eta} U { None }
        Args:
            b (int): an integer in the range 0 - 15.
        Returns:
            z (int): sampled coefficient or 'None' if rejected.
        Raises:
            TypeError: if b is not an integer.
            ValueError: if b is not in the range 0 - 15.
        """
        if not isinstance(b, int):
                raise TypeError (f"{b} must be in an integer.")
        if not (0 <= b <= 15):
                raise ValueError (f"{b} must be in the range 0 - 15.")

        # line 1 and 2: rejection sampling from {-2, ... , 2 }
        if self.eta == 2 and b < 15:
            return 2 - (b % 5)
        
        # line 3: rejection sampling from {-4, ... , 4 }
        elif self.eta == 4 and b < 9:
            return 4 - b
        
        # line 4: sample is just rejected.
        else:
            return None

    def rej_bounded_poly (self, rho: bytes) -> list:
        """
        samples an element a with coefficients in [-eta, eta] computed via rejection sampling from rho.
        Args:
            rho (bytes): a bytestring of length 66.
        Returns:
            a (list): a list of integers representing the polynomial.
        Raises:
            TypeError: if rho is not a bytestring.
        """
        # input checks.
        if not isinstance (rho, (bytes, bytearray)):
            raise TypeError ("expected a bytestring as input.")
        if not (len(rho) == 66):
            raise ValueError ("length of rho must be exactly 66 bytes.")
        
        # line 1: initialize j and polynomial a.
        j = 0
        a = [0 for _ in range(self.N)]

        # line 2: initialize shake_256 ; H.init().
        ctx = hashlib.shake_256() # H.init()

        # line 3: hash rho with the shake_256 object ; # H.Absorb(ctx, rho).
        ctx.update(rho) # H.Absorb(ctx, rho)

        byte_stream = ctx.digest(self.N) # store the hash in byte_stream for faster calling.
        byte_position = 0 # temporary variable to keep track of position in byte_stream.

        # line 4: main rejection loop.
        while j < 256:
            if byte_position + 1 > len(byte_stream): # to prevent byte_stream from going out of index.
                byte_stream += ctx.digest(self.N)
            
            # line 5: take out next byte form the hash ; H.squeeze(ctx, 1).
            z = byte_stream[byte_position]
            byte_position += 1 # update byte position go get next byte on next selection.

            # line 6: sample a number from z.
            z0 = self.coeff_from_half_byte(z % 16)

            # line 7: sample a number from z / 16 (floor).
            z1 = self.coeff_from_half_byte(math.floor(z / 16))
            
            # line 8 to 11: rejection checking for z0.
            if z0 is not None:
                a[j] = z0 # accepted.
                j = j + 1

            # line 12 to 15: rejection checking for z1.
            if z1 is not None and j < 256:
                a[j] = z1 # accepted.
                j = j + 1
        
        # line 17: return the polynomial a
        return a

    def gen_s (self, rho: bytes) -> tuple[list, list]:
        """
        Samples two vector polynomials s1 and s2 such that coefficients are in the interval [-eta, eta]. 
        Args:
            rho (bytes): a bytestring of length 64.
        Returns:
            s1 (list): a list of l polynomials representing the vector s1.
            s2 (list): a list of k polynomials representing the vector s2.
        Raises:
            ValueError: if length of rho is not 64 bytes.
        """
        #input checks.
        if not (len(rho) == 64) and not isinstance(rho, bytes):
            raise ValueError ("rho must be a 64-bytes bytestring.")

        # initialize both s1 and s2.
        s1 = [[0 for _ in range(self.N)] for _ in range (self.l)]
        s2 = [[0 for _ in range(self.N)] for _ in range (self.k)]

        # line 1 to 3: create a polynomial from a 66 byte concatenated bytestring.
        for r in range (self.l):
            s1[r] = self.rej_bounded_poly(rho + self.convert.integer_to_bytes(r, 2))
        
        # line 4 to 6: create a polynomial from a 66 byte concatenated bytestring.
        for s in range (self.k):
            s2[s] = self.rej_bounded_poly(rho + self.convert.integer_to_bytes(s + self.l, 2))
        
        # line 7: return s1 and s2 polynomial vectors.
        return s1, s2
    
    def gen_mask(self, rho: bytes, mu: int):
        """
        Samples a vector y ∈ R^l such that each polynomial y[r] has coefficients between -gamma1 + 1 and gamma1
        Args:
            rho (bytes): a bytestring of length 64.
            mu (int): an integer used in the sampling process.
        Returns:
            y (list): a list of polynomials representing the vector y.
        Raises:
            ValueError: if length of rho is not 64 bytes.
            TypeError: if mu is not an integer.
            ValueError: if mu is a negative integer.
        """
        if not (len(rho) == 64) and not isinstance(rho, bytes):
            raise ValueError ("rho must be a 64-bytes bytestring.")
        if not isinstance(mu, int):
            raise TypeError ("mu must be an integer.")
        if mu < 0:
            raise ValueError ("mu must be a non-negative integer.")

        if self.gamma1 == (1 << 17):
            #bit_count = 18
            total_bytes = 576  # (256 * 18) / 8
        else:
            #bit_count = 20
            total_bytes = 640  # (256 * 20) / 8

        y = [[0 for _ in range (self.N)] for _ in range (self.l+self.k+1)]

        for r in range (self.l+self.k+1):
            rho_prime = rho + self.convert.integer_to_bytes(mu + r, 2)
            v = self.convert.hash(rho_prime, total_bytes)
            y[r] = self.packing.bit_unpack(v, self.gamma1 - 1, self.gamma1)
            
        return y

    def sample_in_ball(self, rho: bytes) -> list:
        """
        Samples a polynomial with coefficients form {-1, 0, 1} and hamming weight tau <= 64.
        Args:
            rho (bytes): a bytestring of length lambda / 4 bits.
        Returns:
            c (list): a list of integers representing the polynomial.
        Raises:
            ValueError: if length of rho is not lambda / 4 bits.
            TypeError: if rho is not a bytestring.
        """
        if not isinstance (rho, (bytes, bytearray)):
            raise TypeError ("expected a bytestring as input.")
        
        c = [0 for _ in range(self.N)]
        ctx = hashlib.shake_256() # H.init()
        ctx.update(rho) # H.Absorb(ctx, rho)

        search_multiplier = 1
        byte_stream = ctx.digest(self.N * search_multiplier) # the amount that we should digest is arbitrary here but will cause differences 

        h = self.convert.bytes_to_bits(byte_stream[:8])

        byte_position = 8
        for i in range(256 - self.tau, 256):
            j = byte_stream[byte_position]
            byte_position = byte_position + 1

            while j > i:
                if byte_position + 1 > len(byte_stream): # to prevent byte_stream from going out of index.
                    search_multiplier = search_multiplier + 1
                    byte_stream = ctx.digest(self.N * search_multiplier)
                j = byte_stream[byte_position]
                byte_position = byte_position + 1
            
            c[i] = c[j]
            if int(h[i + self.tau - 256]) == 1: # taking this as equivalent to being (-1)^h[i+tau-256]
                c[j] = -1
            else:
                c[j] = 1
        
        return c

    

