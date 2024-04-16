from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

# JWT config
JWT_SECRET = "your_jwt_secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_jwt(username: str, secret: str, is_secure: bool):

    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour

    payload = {
        "sub": username,  # Subject, usually the username or user id
        "iat": datetime.utcnow(),  # Issued at time
        "exp": expiration,  # Expiration time
    }

    token = jwt.encode(payload, secret, algorithm=ALGORITHM)

    return token