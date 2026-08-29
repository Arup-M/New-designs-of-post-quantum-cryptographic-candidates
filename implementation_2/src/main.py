from proposal.dsa import *
import secrets
import random
import time

# Mapping security levels and parameter sets to classes
DSA_SCHEMES = {
    (128, 1): DSA_128_1,
    (128, 2): DSA_128_2,
    (192, 1): DSA_192_1,
    (192, 2): DSA_192_2,
    (256, 1): DSA_256_1,
    (256, 2): DSA_256_2,
}

# Function to safely read integer input from a fixed set
def get_valid_input(prompt, valid_values):
    while True:
        try:
            value = int(input(prompt))
            if value in valid_values:
                return value
            else:
                print(f"Invalid input! Valid options are: {valid_values}")
        except ValueError:
            print("Please enter a valid integer.")

security_level = get_valid_input("Enter the security level (128/192/256): ", [128, 192, 256])
parameter_set = get_valid_input("Enter the parameter set (1: Dilithium parameters / 2: New parameters): ", [1, 2])
num_of_exp = int(input("Enter the number of experiments: "))


dsa = DSA_SCHEMES[(security_level, parameter_set)]

print(f"----------------- for security level {security_level} with parameter set {parameter_set} -------------------")

public_key, private_key = dsa.dsa_keygen()
print("public key size:", len(public_key))
print("private key size:", len(private_key))

#num_of_exp = 10
passed = 0
total_sig_size = 0
signing_time = 0

# Run experiments
for _ in range(num_of_exp):
    message = secrets.token_bytes(random.randint(1, 1000))
    # msg=input("Enter message: ")
    # message = msg.encode("utf-8")

    start = time.perf_counter()
    signature = dsa.dsa_sign(private_key, message)
    end = time.perf_counter()

    signing_time += (end - start)
    total_sig_size += len(signature)

    if dsa.dsa_verify(public_key, message, signature):
        passed += 1

signing_time_per_sign = signing_time / num_of_exp
avg_sig_size = total_sig_size / num_of_exp
avg_rejections = dsa.total_num_of_rejections / num_of_exp

print("Average signature size:", avg_sig_size)
print("Average repetitions:", avg_rejections)
print(f"Verification passed: {passed} / {num_of_exp}")
print(f"Signing time: {signing_time_per_sign} seconds")

if passed == num_of_exp:
    print("VERIFICATION SUCCESSFUL")
else:
    print("VERIFICATION FAILED")
