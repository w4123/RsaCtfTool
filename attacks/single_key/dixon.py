#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from attacks.abstract_attack import AbstractAttack
from lib.keys_wrapper import PrivateKey
from lib.exceptions import FactorizationError
from lib.number_theory import (
    isqrt,
    gcd,
    is_prime,
    primes,
    powmod,
    is_square,
    powmod_base_list,
)
import bitarray


def dixon_factor(N, B=7):
    if is_prime(N):
        return N, 1

    if is_square(N):
        i = isqrt(N)
        return i, i

    base = primes(B)
    lqbf = pow(base[-1], 2) + 1
    QBF = bitarray.bitarray(lqbf)  # This is our quasi-bloom-filter

    basej2N = powmod_base_list(base, 2, N)
    for p in basej2N: QBF[p] = 1

    for i in range(isqrt(N), N):
        i2N = powmod(i, 2, N)
        if i2N < lqbf and QBF[i2N] == 1:
            for k in range(0, len(base)):
                # if i2N == basej2N[k]: # this is replaced with a quasi-bloom-filter
                if QBF[basej2N[k]] == 1 and 1 < (f:= gcd(i - base[k], N)) < N:
                    return f, N // f


class Attack(AbstractAttack):
    def __init__(self, timeout=60):
        super().__init__(timeout)
        self.speed = AbstractAttack.speed_enum["slow"]

    def attack(self, publickey, cipher=[], progress=True):
        """Run dixon attack with a timeout"""
        try:
            if publickey.n <= 10_000_000_000:
                publickey.p, publickey.q = dixon_factor(publickey.n)
            else:
                self.logger.error("[-] Dixon is too slow for pubkeys > 10^10...")
                return None, None

        except FactorizationError:
            return None, None

        if publickey.p is not None and publickey.q is not None:
            try:
                priv_key = PrivateKey(
                    n=publickey.n,
                    p=int(publickey.p),
                    q=int(publickey.q),
                    e=int(publickey.e),
                )
                return priv_key, None
            except ValueError:
                return None, None

        return None, None

    def test(self):
        from lib.keys_wrapper import PublicKey

        key_data = """-----BEGIN PUBLIC KEY-----
MCAwDQYJKoZIhvcNAQEBBQADDwAwDAIFAQAwAjcCAwEAAQ==
-----END PUBLIC KEY-----"""
        result = self.attack(PublicKey(key_data), progress=False)
        return result != (None, None)
