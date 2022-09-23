from jose import JWTError, jwt
from datetime import datetime, timedelta

# SECRET_KEY 
# Algorithm 
# Expiration time

SECRET_KEY = "9028u4an3313kjflaj93ruo1089380jkjdfkfff901klajdf09u9c88uaflukl23j"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt