from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

# JWT config
JWT_SECRET = "your_jwt_secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_jwt(user_id: str, secret: str, role: str, is_secure: bool):
    expiration = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours

    payload = {
        "sub": user_id,  # user email
        "iat": datetime.utcnow(),  # Issued at time
        "exp": expiration,  # Expiration time
        "role": role,  # User role
    }

    token = jwt.encode(payload, secret, algorithm=ALGORITHM)
    return token
