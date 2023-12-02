from cryptography.hazmat.primitives import serialization

with open("../private-key.pem", "rb") as key_file:
    private_key = key_file.read()