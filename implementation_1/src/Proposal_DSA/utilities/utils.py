## utils.py

def reduce_mod_pm(n, a):
    """
        It takes an integer n and represents it as an integer in the range.
        For odd {a}:
            {-(a-1)/2 < r <= (a-1)/2}
        for even {a}:
            {- a/2 < r <= a/2}
    """
    r = n % a
    if r > (a >> 1):
        r -= a

    return r

def decompose(r, a, q):
    """
    Takes an element r and represents it as:  r = r1*a + r0
    With r0 in the range -(a << 1) < r0 <= (a << 1)
    """
    rp = r % q
    r0 = reduce_mod_pm(rp, a)
    #r1 = rp - r0
    if rp - r0 == q - 1:
        r1 = 0
        r0 = r0 - 1
    else:
        r1 = (rp - r0) // a

    #assert rp == (r1 * a + r0), f"Decomposition failed: {r} != {r1} * {a} + {r0}"
    return r1, r0


def high_bits(r, a, q):
    r1, _ = decompose(r, a, q)
    return r1


def low_bits(r, a, q):
    _, r0 = decompose(r, a, q)
    return r0

def make_hint(z, r, a, q):
    """
    Check whether the top bit of z will change when r is added
    """
    r1 = high_bits(r, a, q)
    v1 = high_bits(r + z, a, q)
    return int(r1 != v1)

def use_hint(h, r, a, q):
    """
        Use_hint(h, r, a, q)
            Compute the high bits of {(r + z)} using a hint {h}.
        Parameters:
            h (int): a carry hint
            r (int): want to compute the high bits of {(r + z)} using a hint {h}
            a (int): The divisor used in decomposition
            q (int): modulus q.
        Returns:
            int: The result of the computation based on the input parameters.
    """
    m = (q - 1) // a
    r1, r0 = decompose(r, a, q)
    if h == 1:
        if r0 > 0:
            return (r1 + 1) % m
        return (r1 - 1) % m
    return r1



def check_norm_bound(n, b, q):
    """
        Norm bound is checked in the following four steps:
        x ∈ {0, ..., ..., q-1}
        x ∈ {-(q-1)/2, ..., -1, 0, ..., (q-1)/2}
        x ∈ { (q-3)/2, ..., 0, 0, ..., (q-1)/2}
        x ∈ {0, 1, ..., (q-1)/2, (q-1)/2, ..., 1}
    """
    x = n % q
    x = ((q - 1) >> 1) - x
    x = x ^ (x >> 31)
    x = ((q - 1) >> 1) - x
    return x >= b


def xor_bytes(a, b):
    """
    XOR two byte arrays, assume that they are
    of the same length
    """
    return bytes(a ^ b for a, b in zip(a, b))
