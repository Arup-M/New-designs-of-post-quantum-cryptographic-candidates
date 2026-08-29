import unittest
import json
# import secrets
# import random
from src.Proposal_DSA.mldsa.mldsa import *
#from src.proposal.dsa import DSA_128_1, DSA_128_2, DSA_192_1, DSA_192_2, DSA_256_1, DSA_256_2

# declaring the parameters
# dsa2 = MLDSA(q=8380417,q_len=23,n=256,root_of_unity=1753,d=13,k=4,l=4,eta=2,tau=39,omega=80,gamma_1=131072,
#         gamma_2=95232)
dsa2 = MLDSA(q=8383489,q_len=23,n=256,root_of_unity=11998,d=13,k=4,l=4,eta=2,tau=40,omega=90,gamma_1=131072,
        gamma_2=87328)
# gamma1= 2^17 , gamma2=(q-1)/96

# dsa3 = MLDSA(q=8380417,q_len=23,n=256,root_of_unity=1753,d=13,k=6,l=5,eta=2,tau=49,omega=55,gamma_1=524288,
#         gamma_2=261888)
dsa3 = MLDSA(q=8383489,q_len=23,n=256,root_of_unity=11998,d=13,k=6,l=5,eta=4,tau=50,omega=56,gamma_1=524288,
        gamma_2=261984)
# gamma1= 2^19 , gamma2=(q-1)/32

# dsa5 = MLDSA(q=8380417,q_len=23,n=256,root_of_unity=1753,d=13,k=8,l=7,eta=2,tau=60,omega=75,gamma_1=524288,
#         gamma_2=261888)
dsa5 = MLDSA(q=8383489,q_len=23,n=256,root_of_unity=11998,d=13,k=8,l=7,eta=2,tau=59,omega=70,gamma_1=524288,
        gamma_2=261984)
# gamma1= 2^19 , gamma2=(q-1)/32

class TestDSA(unittest.TestCase):
    """
    Test ML DSA for internal consistency by generating signatures
    and verifying them!
    """

    def generic_test_dsa(self, proposal):
        msg = b"Signed by proposal signature scheme" + secrets.token_bytes(random.randint(1, 1000))

        # Perform signature process
        pk, sk = proposal.keygen()
        sig,_ = proposal.sign(sk, msg)
        check_verify = proposal.verify(pk, msg, sig)

        # Generate some fail cases
        pk_bad, _ = proposal.keygen()
        check_wrong_pk = proposal.verify(pk_bad, msg, sig)
        check_wrong_msg = proposal.verify(pk, b"wrong message", sig)

        # Check that signature works
        self.assertTrue(check_verify)
        # Check changing the key breaks verify
        self.assertFalse(check_wrong_pk)
        # Check changing the message breaks verify
        self.assertFalse(check_wrong_msg)

    def test_dsa2(self):
        for _ in range(5):
            self.generic_test_dsa(dsa2)

    def test_dsa3(self):
        for _ in range(5):
            self.generic_test_dsa(dsa3)

    def test_dsa5(self):
        for _ in range(5):
            self.generic_test_dsa(dsa5)


class TestMLDSADeterministic(unittest.TestCase):
    """
    Test ML DSA for internal consistency by generating signatures
    and verifying them!
    """

    def generic_test_dsa(self, dsa, count=5):
        for _ in range(count):
            msg = b"Signed by proposal signature scheme" + secrets.token_bytes(random.randint(1, 1000))

            # Perform signature process
            pk, sk = dsa.keygen()
            sig,_ = dsa.sign(sk, msg)
            check_verify = dsa.verify(pk, msg, sig)

            # Generate some fail cases
            pk_bad, _ = dsa.keygen()
            check_wrong_pk = dsa.verify(pk_bad, msg, sig)
            check_wrong_msg = dsa.verify(pk, b"asdfghjkl", sig)

            # Check that signature works
            self.assertTrue(check_verify)

            # Check changing the key breaks verify
            self.assertFalse(check_wrong_pk)

            # Check changing the message breaks verify
            self.assertFalse(check_wrong_msg)

    def test_dsa2(self):
        self.generic_test_dsa(dsa2)

    def test_dsa3(self):
        self.generic_test_dsa(dsa3)

    def test_dsa5(self):
        self.generic_test_dsa(dsa5)

class TestDsaKat(unittest.TestCase):

    def generic_keygen_kat(self, dsa, index):
        with open("assets/DSA-KeyGen/internalProjection.json") as f:
            data = json.load(f)
        kat_data = data["testGroups"][index]["tests"]

        for test in kat_data:
            seed = bytes.fromhex(test["seed"])
            pk_kat = bytes.fromhex(test["pk"])
            sk_kat = bytes.fromhex(test["sk"])

            pk, sk = dsa.keygen(seed)
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

            sig,_ = dsa.sign(sk_kat, msg_kat, random_bit_kat)
            # print("sig:\n", sig)
            # print("sig_kat:\n", sig_kat)
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

            check = dsa.verify(pk_kat, msg_kat, sig_kat)
            print(check, " ", check_kat)
            self.assertEqual(check, check_kat)

    # def test_dsa2_keygen(self):
    #     self.generic_keygen_kat(dsa2, 0)

    def test_dsa2_keygen(self):
        self.generic_keygen_kat(dsa2, 1)

    # def test_dsa3_keygen(self):
    #     self.generic_keygen_kat(dsa3, 2)

    def test_dsa3_keygen(self):
        self.generic_keygen_kat(dsa3, 3)

    # def test_dsa5_keygen(self):
    #     self.generic_keygen_kat(dsa5, 4)

    def test_dsa5_keygen(self):
        self.generic_keygen_kat(dsa5, 5)

    # def test_dsa2_sign(self):
    #     self.generic_sign_kat(dsa2, 0)

    def test_dsa2_sign(self):
        self.generic_sign_kat(dsa2, 1)

    # def test_dsa3_sign(self):
    #     self.generic_sign_kat(dsa3, 2)

    def test_dsa3_sign(self):
        self.generic_sign_kat(dsa3, 3)

    # def test_dsa5_sign(self):
    #     self.generic_sign_kat(dsa5, 4)

    def test_dsa5_sign(self):
        self.generic_sign_kat(dsa5, 5)

    # def test_dsa2_verify(self):
    #     self.generic_verify_kat(dsa2, 0)

    def test_dsa2_verify(self):
        self.generic_verify_kat(dsa2, 1)

    # def test_dsa3_verify(self):
    #     self.generic_verify_kat(dsa3, 2)

    def test_dsa3_verify(self):
        self.generic_verify_kat(dsa3, 3)

    # def test_dsa5_verify(self):
    #     self.generic_verify_kat(dsa5, 4)

    def test_dsa5_verify(self):
        self.generic_verify_kat(dsa5, 5)
