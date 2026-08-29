from .dsa import DSA


DEFAULT_PARAMETERS_1 = {
    "DSA_128": {
        "q": 8380417, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 4, # no. of rows in A
        "l": 4, # no. of columns in A
        "eta": 2, # private key range
        "gamma1": 131072, # coefficient range of y
        "gamma2": 95232, # low order rounding range
        "tau": 39,  # number of ±1s in c
        "omega": 80,  # Max number of 1s in hint
    },
    "DSA_192": {
        "q": 8380417, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 6, # no. of rows in A
        "l": 5, # no. of columns in A
        "eta": 4, # private key range
        "gamma1": 524288, # coefficient range of y
        "gamma2": 261888, # low order rounding range
        "tau": 49,  # number of ±1s in c
        "omega": 55,  # Max number of 1s in hint
    },
    "DSA_256": {
        "q": 8380417, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 8, # no. of rows in A
        "l": 7, # no. of columns in A
        "eta": 2, # private key range
        "gamma1": 524288, # coefficient range of y
        "gamma2": 261888, # low order rounding range
        "tau": 60,  # number of ±1s in c
        "omega": 75,  # Max number of 1s in hint
    },
}

DEFAULT_PARAMETERS_2 = {
    "DSA_128": {
        "q": 8383489, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 4, # no. of rows in A
        "l": 4, # no. of columns in A
        "eta": 2, # private key range
        "gamma1": 131072, # coefficient range of y # 2**17
        "gamma2": 87328, # low order rounding range #(q-1)/96
        "tau": 36,  # number of ±1s in c
        "omega": 90,  # Max number of 1s in hint
    },
    "DSA_192": {
        "q": 8383489, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 6, # no. of rows in A
        "l": 5, # no. of columns in A
        "eta": 4, # private key range
        "gamma1": 524288, # coefficient range of y #2**19
        "gamma2": 261984, # low order rounding range #(q-1)/32
        "tau": 45,  # number of ±1s in c
        "omega": 56,  # Max number of 1s in hint
    },
    "DSA_256": {
        "q": 8383489, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 8, # no. of rows in A
        "l": 7, # no. of columns in A
        "eta": 2, # private key range
        "gamma1": 524288, # coefficient range of y #2**19
        "gamma2": 261984, # low order rounding range #(q-1)/32
        "tau": 60,  # number of ±1s in c
        "omega": 70,  # Max number of 1s in hint
    },
}

DSA_128_1 = DSA(DEFAULT_PARAMETERS_1["DSA_128"])
DSA_192_1 = DSA(DEFAULT_PARAMETERS_1["DSA_192"])
DSA_256_1 = DSA(DEFAULT_PARAMETERS_1["DSA_256"])

DSA_128_2 = DSA(DEFAULT_PARAMETERS_2["DSA_128"])
DSA_192_2 = DSA(DEFAULT_PARAMETERS_2["DSA_192"])
DSA_256_2 = DSA(DEFAULT_PARAMETERS_2["DSA_256"])

