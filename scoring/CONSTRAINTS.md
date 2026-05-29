# Constraints

- Use the same generated benchmark from `data/generate_synthetic.py`.
- Keep embedding dimension fixed at 512.
- Do not train a classifier or surrogate model to map queries to identities.
- Evaluation must consume prediction artifacts written by `method/` or `baseline/`.
- IDFace-family methods must use top-magnitude ternary transformation, positive/negative splitting, base-`p` packing, additive database inner products, and decoding.
- Encrypted IDFace variants must store packed enrolled templates as randomized ciphertexts and recover scores only after homomorphic accumulation and decryption.
