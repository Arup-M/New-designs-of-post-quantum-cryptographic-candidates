# New designs of post-quantum cryptographic candidates

Python research implementations of module-lattice digital signature proposals. The code explores Dilithium-style constructions and alternative parameter choices through key generation, signing, verification, and experiments measuring key sizes, signature sizes, signing time, and sampling repetitions.

## Repository structure

| Directory | Contents |
| --- | --- |
| [`implementation_1/`](implementation_1/) | A configurable `MLDSA` implementation built around polynomial-ring and module classes. |
| [`implementation_2/`](implementation_2/) | A `DSA` implementation with six predefined instances covering two parameter families. |
| `implementation_*/src/main.py` | Interactive experiment runners. |
| `implementation_*/tests/test_dsa.py` | Signature consistency checks and known-answer tests. |
| `implementation_*/assets/` | Bundled proposal test vectors for key generation, signing, and verification. |

Both implementations contain SHAKE hashing, sampling, number-theoretic transforms (NTT), polynomial arithmetic, and key/signature encoding. Their APIs and parameter definitions differ, so the examples below treat them separately.

## Getting started

Use **Python 3.9 or newer**. The core code can run with the Python standard library. Implementation 1 optionally uses `xoflib` when available and otherwise uses its bundled SHAKE wrapper. Its original dependency list is retained in [`implementation_1/src/requirements.txt`](implementation_1/src/requirements.txt).

```sh
git clone https://github.com/Arup-M/New-designs-of-post-quantum-cryptographic-candidates.git
cd New-designs-of-post-quantum-cryptographic-candidates
```

The commands below assume this repository is your starting directory. No package installation is needed for the standard-library examples or `unittest` commands.

## Implementation 1

Run the interactive experiment:

```sh
cd implementation_1
python src/main.py
```

Enter a **positive number of experiments**. The runner evaluates three configurations and reports public/secret key lengths, average signature size, average signing time, average signing attempts, and whether all signatures verified.

The demo configurations share `q = 8383489`, `n = 256`, `root_of_unity = 11998`, and `d = 13`:

| Demo instance | k | l | eta | tau | omega |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dsa2` | 4 | 4 | 2 | 36 | 90 |
| `dsa3` | 6 | 5 | 4 | 45 | 56 |
| `dsa5` | 8 | 7 | 2 | 60 | 70 |

Complete demo parameters are defined in [`implementation_1/src/main.py`](implementation_1/src/main.py). The tests use different `tau` values: `40`, `50`, and `59`, respectively. The `default_parameters.py` file is commented out; construct `MLDSA` explicitly.

Example, with `implementation_1/` as the working directory:

```python
from src.Proposal_DSA.mldsa.mldsa import MLDSA

dsa = MLDSA(
    q=8383489, q_len=23, n=256, root_of_unity=11998,
    d=13, k=4, l=4, eta=2, tau=36, omega=90,
    gamma_1=131072, gamma_2=87328,
)

message = b"Example message"
public_key, secret_key = dsa.keygen()
signature, attempts = dsa.sign(secret_key, message)

assert dsa.verify(public_key, message, signature)
assert not dsa.verify(public_key, b"Modified message", signature)
```

`sign()` returns both the encoded signature and the number of signing attempts.

## Implementation 2

From the repository root:

```sh
cd implementation_2
python src/main.py
```

The runner prompts for a parameter label (`128`, `192`, or `256`), a parameter family (`1` or `2`), and a **positive number of experiments**. It reports key sizes, average signature size, average sampling repetitions, average signing time, and the number of successful verifications.

Family 1 is labelled **Dilithium parameters** in the runner; family 2 is labelled **New parameters**. All instances use polynomial degree `N = 256` and rounding parameter `d = 13`.

| Exported instance | Family | Modulus q | (k, l) | tau | omega |
| --- | ---: | ---: | --- | ---: | ---: |
| `DSA_128_1` | 1 | 8380417 | (4, 4) | 39 | 80 |
| `DSA_192_1` | 1 | 8380417 | (6, 5) | 49 | 55 |
| `DSA_256_1` | 1 | 8380417 | (8, 7) | 60 | 75 |
| `DSA_128_2` | 2 | 8383489 | (4, 4) | 36 | 90 |
| `DSA_192_2` | 2 | 8383489 | (6, 5) | 45 | 56 |
| `DSA_256_2` | 2 | 8383489 | (8, 7) | 60 | 70 |

The complete definitions, including `eta`, `gamma1`, and `gamma2`, are in [`implementation_2/src/proposal/dsa/default_parameters.py`](implementation_2/src/proposal/dsa/default_parameters.py). The numeric instance names are parameter labels used by this project.

Example, with `implementation_2/` as the working directory:

```python
from src.proposal.dsa import DSA_128_2

message = b"Example message"
public_key, secret_key = DSA_128_2.dsa_keygen()
signature = DSA_128_2.dsa_sign(secret_key, message)

assert DSA_128_2.dsa_verify(public_key, message, signature)
assert not DSA_128_2.dsa_verify(public_key, b"Modified message", signature)
```

Unlike implementation 1, `dsa_sign()` returns the signature alone.

## Tests

Run tests from **inside the implementation directory** being tested. Fixture paths are relative to that directory.

For signature consistency checks, including rejection of a wrong public key or modified message:

```sh
python -m unittest tests.test_dsa.TestDSA tests.test_dsa.TestMLDSADeterministic
```

To include the bundled known-answer vectors:

```sh
python -m unittest discover -s tests -v
```

The files named `src/test.py` are standalone experiment scripts; the test suites are in `tests/`. The bundled vectors identify their revision as `Proposal` and should be interpreted as proposal fixtures.

## Research status

These are experimental signature proposals with custom constructions and parameter choices. The parameter labels and bundled tests do not establish security levels or standardized ML-DSA conformance. Signing also uses Python's `random` module for a sign choice; this repository is intended for research and experimentation.

## License

Released under the [MIT License](LICENSE).
