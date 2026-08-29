import unittest
import json
import secrets
import random
from src.proposal.dsa import DSA_128_1, DSA_128_2, DSA_192_1, DSA_192_2, DSA_256_1, DSA_256_2


class TestDSA(unittest.TestCase):
    """
    Test ML DSA for internal consistency by generating signatures
    and verifying them!
    """

    def generic_test_dsa(self, proposal):
        msg = b"Signed by proposal signature scheme" + secrets.token_bytes(random.randint(1, 1000))

        # Perform signature process
        pk, sk = proposal.dsa_keygen()
        sig = proposal.dsa_sign(sk, msg)
        check_verify = proposal.dsa_verify(pk, msg, sig)

        # Generate some fail cases
        pk_bad, _ = proposal.dsa_keygen()
        check_wrong_pk = proposal.dsa_verify(pk_bad, msg, sig)
        check_wrong_msg = proposal.dsa_verify(pk, b"wrong message", sig)

        # Check that signature works
        self.assertTrue(check_verify)
        # Check changing the key breaks verify
        self.assertFalse(check_wrong_pk)
        # Check changing the message breaks verify
        self.assertFalse(check_wrong_msg)

    def test_DSA_128_1(self):
        for _ in range(5):
            self.generic_test_dsa(DSA_128_1)

    def test_DSA_128_2(self):
        for _ in range(5):
            self.generic_test_dsa(DSA_128_2)

    def test_DSA_192_1(self):
        for _ in range(5):
            self.generic_test_dsa(DSA_192_1)

    def test_DSA_192_2(self):
        for _ in range(5):
            self.generic_test_dsa(DSA_192_2)

    def test_DSA_256_1(self):
        for _ in range(5):
            self.generic_test_dsa(DSA_256_1)

    def test_DSA_256_2(self):
        for _ in range(5):
            self.generic_test_dsa(DSA_256_2)


class TestMLDSADeterministic(unittest.TestCase):
    """
    Test ML DSA for internal consistency by generating signatures
    and verifying them!
    """

    def generic_test_dsa(self, dsa, count=5):
        for _ in range(count):
            msg = b"Signed by proposal signature scheme" + secrets.token_bytes(random.randint(1, 1000))

            # Perform signature process
            pk, sk = dsa.dsa_keygen()
            sig = dsa.dsa_sign(sk, msg)
            check_verify = dsa.dsa_verify(pk, msg, sig)

            # Generate some fail cases
            pk_bad, _ = dsa.dsa_keygen()
            check_wrong_pk = dsa.dsa_verify(pk_bad, msg, sig)
            check_wrong_msg = dsa.dsa_verify(pk, b"asdfghjkl", sig)

            # Check that signature works
            self.assertTrue(check_verify)

            # Check changing the key breaks verify
            self.assertFalse(check_wrong_pk)

            # Check changing the message breaks verify
            self.assertFalse(check_wrong_msg)

    def test_DSA_128_1(self):
        self.generic_test_dsa(DSA_128_1)

    def test_DSA_128_2(self):
        self.generic_test_dsa(DSA_128_2)

    def test_DSA_192_1(self):
        self.generic_test_dsa(DSA_192_1)

    def test_DSA_192_2(self):
        self.generic_test_dsa(DSA_192_2)

    def test_DSA_256_1(self):
        self.generic_test_dsa(DSA_256_1)

    def test_DSA_256_2(self):
        self.generic_test_dsa(DSA_256_2)

class TestDsaKat(unittest.TestCase):
    """
    Test ML-DSA against test vectors collected from
    https://github.com/usnistgov/ACVP-Server/releases/tag/v1.1.0.35
    """

    def generic_keygen_kat(self, dsa, index):
        with open("assets/DSA-KeyGen/internalProjection.json") as f:
            data = json.load(f)
        kat_data = data["testGroups"][index]["tests"]

        for test in kat_data:
            seed = bytes.fromhex(test["seed"])
            pk_kat = bytes.fromhex(test["pk"])
            sk_kat = bytes.fromhex(test["sk"])

            pk, sk = dsa.dsa_keygen(seed)
            self.assertEqual(pk, pk_kat)
            self.assertEqual(sk, sk_kat)

    def generic_sign_kat(self, dsa, index):
        with open("assets/DSA-SigGen/internalProjection.json") as f:
            data = json.load(f)
            kat_data = data["testGroups"][index]["tests"]

        for test in kat_data:
            sk_kat = bytes.fromhex(test["sk"])
            msg_kat = bytes.fromhex(test["message"])
            sig_kat = bytes.fromhex(test["signature"])
            random_bit_kat = test["random_bit"]

            sig = dsa.dsa_sign(sk_kat, msg_kat, random_bit_kat)
            self.assertEqual(sig, sig_kat)



    def generic_verify_kat(self, dsa, index):
        with open("assets/DSA-SigVer/internalProjection.json") as f:
            data = json.load(f)
        pk_kat = bytes.fromhex(data["testGroups"][index]["pk"])
        kat_data = data["testGroups"][index]["tests"]

        for test in kat_data:
            check_kat = test["testPassed"]
            msg_kat = bytes.fromhex(test["message"])
            sig_kat = bytes.fromhex(test["signature"])

            check = dsa.dsa_verify(pk_kat, msg_kat, sig_kat)
            print(check, " ", check_kat)
            self.assertEqual(check, check_kat)

    def test_DSA_128_1_keygen(self):
        self.generic_keygen_kat(DSA_128_1, 0)

    def test_DSA_128_2_keygen(self):
        self.generic_keygen_kat(DSA_128_2, 1)

    def test_DSA_192_1_keygen(self):
        self.generic_keygen_kat(DSA_192_1, 2)

    def test_DSA_192_2_keygen(self):
        self.generic_keygen_kat(DSA_192_2, 3)

    def test_DSA_256_1_keygen(self):
        self.generic_keygen_kat(DSA_256_1, 4)

    def test_DSA_256_2_keygen(self):
        self.generic_keygen_kat(DSA_256_2, 5)

    def test_DSA_128_1_sign(self):
        self.generic_sign_kat(DSA_128_1, 0)

    def test_DSA_128_2_sign(self):
        self.generic_sign_kat(DSA_128_2, 1)

    def test_DSA_192_1_sign(self):
        self.generic_sign_kat(DSA_192_1, 2)

    def test_DSA_192_2_sign(self):
        self.generic_sign_kat(DSA_192_2, 3)

    def test_DSA_256_1_sign(self):
        self.generic_sign_kat(DSA_256_1, 4)

    def test_DSA_256_2_sign(self):
        self.generic_sign_kat(DSA_256_2, 5)

    def test_DSA_128_1_verify(self):
        self.generic_verify_kat(DSA_128_1, 0)

    def test_DSA_128_2_verify(self):
        self.generic_verify_kat(DSA_128_2, 1)

    def test_DSA_192_1_verify(self):
        self.generic_verify_kat(DSA_192_1, 2)

    def test_DSA_192_2_verify(self):
        self.generic_verify_kat(DSA_192_2, 3)

    def test_DSA_256_1_verify(self):
        self.generic_verify_kat(DSA_256_1, 4)

    def test_DSA_256_2_verify(self):
        self.generic_verify_kat(DSA_256_2, 5)
