# test_bcrypt.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd_context.hash("1234")
print("Hash:", hashed)
print("Verify:", pwd_context.verify("1234", hashed))