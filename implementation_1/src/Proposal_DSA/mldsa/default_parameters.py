# from .mldsa import MLDSA
#
# DEFAULT_PARAMETERS = {
#     "dsa2": {
#         "q": 8383489,
#         "q_len": 23,
#         "n": 256,
#         "root_of_unity": 11998,
#         "d": 13,
#         "k": 4,
#         "l": 4,
#         "eta": 2,
#         "tau": 40,
#         "omega": 90,
#         "gamma_1": 131072,  # 2^17
#         "gamma_2": 87328,  # (q-1)/96
#     },
#     "dsa3": {
#         "q": 8383489,
#         "q_len": 23,
#         "n": 256,
#         "root_of_unity": 11998,
#         "d": 13,
#         "k": 6,
#         "l": 5,
#         "eta": 4,
#         "tau": 50,
#         "omega": 56,
#         "gamma_1": 524288,  # 2^19
#         "gamma_2": 261984,  # (q-1)/32
#     },
#     "dsa5": {
#         "q": 8383489,
#         "q_len": 23,
#         "n": 256,
#         "root_of_unity": 11998,
#         "d": 13,
#         "k": 8,
#         "l": 7,
#         "eta": 2,
#         "tau": 59,
#         "omega": 70,
#         "gamma_1": 524288,  # 2^19
#         "gamma_2": 261984,  # (q-1)/32
#     },
# }
#
# dsa2 = MLDSA(DEFAULT_PARAMETERS["dsa2"])
# dsa3 = MLDSA(DEFAULT_PARAMETERS["dsa3"])
# dsa5 = MLDSA(DEFAULT_PARAMETERS["dsa5"])
#
# # print()
# # def prime_ntt(q, n):  # check if prime is ntt_friendly
# #     if q % (n << 1) == 1:
# #         return True
# #     else:
# #         raise ValueError("prime not ntt-friendly")
# #
# # def set_params(name):
# #     print(f"Enter parameters for {name}:")
# #     params = {}
# #     params['q'] = int(input("q:"))
# #     params['n'] = int(input("n:"))
# #     prime_ntt(params['q'],params['n'])
# #     params["d"] = int(input("d: "))
# #     params["k"] = int(input("k: "))
# #     params["l"] = int(input("l: "))
# #     params["eta"] = int(input("eta: "))
# #     params["tau"] = int(input("tau: "))
# #     params["omega"] = int(input("omega: "))
# #     params["gamma_1"] = int(input("gamma_1: "))
# #     params["gamma_2"] = int(input("gamma_2: "))
# #     return params
# #
# # #print("---------------- Security level 2 / 3 / 5 -----------------------------")
# # #level=int(input("Enter security level :"))
# #
# # # collecting all parameters
# # DEFAULT_PARAMETERS = {}
# #
# # # if level == 2:
# # #     print(f"---------------------- Security level {level}----------------------------")
# # #     #for param in ["DSA2"]:
# # #     DEFAULT_PARAMETERS["DSA2"] = set_params("DSA2")
# # # elif level == 3:
# # #     print(f"---------------------- Security level {level}----------------------------")
# # #     DEFAULT_PARAMETERS["DSA3"] = set_params("DSA3")
# # #
# # # elif level == 5:
# # #     print(f"---------------------- Security level {level}----------------------------")
# # #     DEFAULT_PARAMETERS["DSA5"] = set_params("DSA5")
# # #
# # # else:
# # #     print(" Security level should be either 2, 3 or 5.")
# #
# #
# # for  param in ["DSA2"]:
# #     DEFAULT_PARAMETERS[param]=set_params(param)
# #
# # # security level 2
# # DSA2 = DSA(DEFAULT_PARAMETERS["DSA2"])
# #
# # # # security level 3
# # # DSA3 = DSA(DEFAULT_PARAMETERS["DSA3"])
# # #
# # # # security level 5
# # # DSA5 = DSA(DEFAULT_PARAMETERS["DSA5"])