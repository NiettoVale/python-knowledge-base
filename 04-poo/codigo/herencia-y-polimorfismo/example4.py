#!/usr/bin/env python3
from abc import ABC, abstractmethod

class AuthMethod(ABC):
    def __init__(self, usuario):
        self.usuario = usuario

    @abstractmethod
    def authenticate(self, credential: str) -> bool:
        pass


class PasswordAuth(AuthMethod):
    def authenticate(self, credential: str) -> bool:
        return credential == "4dm1n"


class OTPAuth(AuthMethod):
    def authenticate(self, credential: str) -> bool:
        return credential == "123456"


class BiometricAuth(AuthMethod):
    def authenticate(self, credential: str) -> bool:
        return credential == "face_scan_8x91k"


def login(auth_method: AuthMethod, credential: str):
    if auth_method.authenticate(credential):
        print(f"[OK] {auth_method.__class__.__name__} - usuario {auth_method.usuario}")
    else:
        print(f"[FAIL] {auth_method.__class__.__name__} - usuario {auth_method.usuario}")


if __name__ == "__main__":
    usuario = "zeta"

    auth_methods = [
        PasswordAuth(usuario),
        OTPAuth(usuario),
        BiometricAuth(usuario),
    ]

    credentials = {
        "PasswordAuth": "4dm1ns",
        "OTPAuth": "1234562",
        "BiometricAuth": "face_scan_8x91ks",
    }

    for auth in auth_methods:
        login(auth, credentials[auth.__class__.__name__])