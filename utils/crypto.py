import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SECRET = os.getenv("COOKIE_SECRET", "SunloMusic_Ultimate_Key").encode()
SALT = b'sunlo_salt_999'
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=100000)
KEY = base64.urlsafe_b64encode(kdf.derive(SECRET))
cipher = Fernet(KEY)

def encrypt_cookie(data: str) -> str: return cipher.encrypt(data.encode()).decode()
def decrypt_cookie(enc_data: str) -> str:
    try: return cipher.decrypt(enc_data.encode()).decode()
    except: return None
