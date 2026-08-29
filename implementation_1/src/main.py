from Proposal_DSA.mldsa.mldsa import *
import time
import secrets

# dsa2 = MLDSA(q=8380417,q_len=23,n=256,root_of_unity=1753,d=13,k=4,l=4,eta=2,tau=39,omega=80,gamma_1=131072,
#         gamma_2=95232)
dsa2 = MLDSA(q=8383489,q_len=23,n=256,root_of_unity=11998,d=13,k=4,l=4,eta=2,tau=36,omega=90,gamma_1=131072,
        gamma_2=87328)
# gamma1= 2^17 , gamma2=(q-1)/96

# dsa3 = MLDSA(q=8380417,q_len=23,n=256,root_of_unity=1753,d=13,k=6,l=5,eta=2,tau=49,omega=55,gamma_1=524288,
#         gamma_2=261888)
dsa3 = MLDSA(q=8383489,q_len=23,n=256,root_of_unity=11998,d=13,k=6,l=5,eta=4,tau=45,omega=56,gamma_1=524288,
        gamma_2=261984)
# gamma1= 2^19 , gamma2=(q-1)/32

# dsa5 = MLDSA(q=8380417,q_len=23,n=256,root_of_unity=1753,d=13,k=8,l=7,eta=2,tau=60,omega=75,gamma_1=524288,
#         gamma_2=261888)
dsa5 = MLDSA(q=8383489,q_len=23,n=256,root_of_unity=11998,d=13,k=8,l=7,eta=2,tau=60,omega=70,gamma_1=524288,
        gamma_2=261984)
# gamma1= 2^19 , gamma2=(q-1)/32

#msg_length = random.randint(10, 100)
#msg_bytes = dsa2.random_bytes(msg_length)
# msg = "Hello World!"
# msg_bytes = msg.encode("utf-8")
"""
    If we use msg = b"Hello World!", msg.encode("utf-8") is not needed.
    But if we use msg = "Hello World!", msg.encode("utf-8") is needed.
"""
num_of_exp = int(input("Enter the number of experiments:"))

print("\n------------------ MLDSA2 ----------------\n")

dsa = dsa2
pk, sk = dsa.keygen()
print("public key length:", len(pk))
print("secret key length:", len(sk))
passed = 0
signing_time = 0
sig_size = 0
num_of_rep = 0

for _ in range (num_of_exp):
    msg = secrets.token_bytes(random.randint(1, 1000))
    start = time.perf_counter()
    sig, rep = dsa.sign(sk, msg)
    end = time.perf_counter()
    signing_time += (end-start)
    sig_size += len(sig)
    num_of_rep += rep

    if dsa.verify(pk, msg, sig):
        passed += 1

if passed == num_of_exp:
    print(f"SIGNATURE SUCCESSFULLY VERIFIED.")

print(f"Signing time per signature: {signing_time / num_of_exp} \nAverage signature size: {sig_size / num_of_exp} \nAverage repetiton: {num_of_rep / num_of_exp}")

print("\n------------------ MLDSA3 ----------------\n")

dsa=dsa3
pk, sk = dsa.keygen()
print("public key length:", len(pk))
print("secret key length:", len(sk))
passed = 0
signing_time = 0
sig_size = 0
num_of_rep = 0

for _ in range (num_of_exp):
    msg = secrets.token_bytes(random.randint(1, 1000))
    start = time.perf_counter()
    sig, rep = dsa.sign(sk, msg)
    end = time.perf_counter()
    signing_time += (end-start)
    sig_size += len(sig)
    num_of_rep += rep

    if dsa.verify(pk, msg, sig):
        passed += 1

if passed == num_of_exp:
    print(f"SIGNATURE SUCCESSFULLY VERIFIED.")

print(f"Signing time per signature: {signing_time / num_of_exp} \nAverage signature size: {sig_size / num_of_exp} \nAverage repetiton: {num_of_rep / num_of_exp}")


print("\n------------------ MLDSA5 ----------------\n")

dsa = dsa5
pk, sk = dsa.keygen()
print("public key length:", len(pk))
print("secret key length:", len(sk))
passed = 0
signing_time = 0
sig_size = 0
num_of_rep = 0

for _ in range (num_of_exp):
    msg = secrets.token_bytes(random.randint(1, 1000))
    start = time.perf_counter()
    sig, rep = dsa.sign(sk, msg)
    end = time.perf_counter()
    signing_time += (end-start)
    sig_size += len(sig)
    num_of_rep += rep

    if dsa.verify(pk, msg, sig):
        passed += 1

if passed == num_of_exp:
    print(f"SIGNATURE SUCCESSFULLY VERIFIED.")

print(f"Signing time per signature: {signing_time / num_of_exp} \nAverage signature size: {sig_size / num_of_exp} \nAverage repetiton: {num_of_rep / num_of_exp}")


