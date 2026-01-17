# auth_utils.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        return False
    #return pwd_context.verify(plain_password, hashed_password)
    return plain_password==hashed_password

def get_password_hash(password: str) -> str:
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    #return pwd_context.hash(password)
    return password