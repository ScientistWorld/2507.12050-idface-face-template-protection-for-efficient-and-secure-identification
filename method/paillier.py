"""Small Paillier cryptosystem used for an encrypted IDFace smoke test.

The paper's large-scale timings use optimized HE libraries. This module keeps
the same additive-homomorphic semantics in pure Python so the portable gym can
exercise real randomized encrypted template storage without external services.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd, lcm
import secrets


def _is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in (2, 3, 5, 7, 11, 13, 17):
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _random_prime(bits: int) -> int:
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if _is_probable_prime(candidate):
            return candidate


@dataclass(frozen=True)
class PaillierPublicKey:
    n: int

    @property
    def n2(self) -> int:
        return self.n * self.n

    def encrypt(self, m: int) -> int:
        if not 0 <= m < self.n:
            raise ValueError("Paillier plaintext out of range")
        while True:
            r = secrets.randbelow(self.n)
            if r > 0 and gcd(r, self.n) == 1:
                break
        return ((1 + self.n * m) * pow(r, self.n, self.n2)) % self.n2

    def add(self, a: int, b: int) -> int:
        return (a * b) % self.n2

    def mul_plain(self, a: int, k: int) -> int:
        if k < 0:
            raise ValueError("negative scalar multiplication is not used by IDFace")
        if k == 0:
            return self.encrypt(0)
        return pow(a, k, self.n2)


@dataclass(frozen=True)
class PaillierPrivateKey:
    public_key: PaillierPublicKey
    lam: int
    mu: int

    def decrypt(self, c: int) -> int:
        n = self.public_key.n
        u = pow(c, self.lam, n * n)
        return (((u - 1) // n) * self.mu) % n


def generate_keypair(bits: int = 256) -> tuple[PaillierPublicKey, PaillierPrivateKey]:
    if bits < 128:
        raise ValueError("use at least 128 bits for the Paillier smoke test")
    half = bits // 2
    p = _random_prime(half)
    q = _random_prime(bits - half)
    while q == p:
        q = _random_prime(bits - half)
    n = p * q
    lam = lcm(p - 1, q - 1)
    u = pow(1 + n, lam, n * n)
    mu = pow((u - 1) // n, -1, n)
    public = PaillierPublicKey(n)
    return public, PaillierPrivateKey(public, lam, mu)
