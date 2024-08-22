import os

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto import Random
from Crypto.Cipher import AES

# from .io import *

# SOURCE: https://www.quickprogrammingtips.com/python/aes-256-encryption-and-decryption-in-python.html
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def genAesKey(size=32):
    return os.urandom(size)
    
def encrypt_aes(raw, key):
    raw = pad(raw)
    raw = raw.encode('utf8')

    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(raw), iv
  
def decrypt_aes(enc, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(enc)
    return unpad(decrypted).decode()

# def genKey():
#     return RSA.generate(2048)
