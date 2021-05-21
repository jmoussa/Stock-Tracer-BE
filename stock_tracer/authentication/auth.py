import json
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from stock_tracer.database import crud, models, database, schemas
from pydantic import BaseModel
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import logging
from stock_tracer.config import config

logger = logging.getLogger(__name__)
# TOKEN Management
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str
    user: schemas.User


class TokenData(BaseModel):
    email: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Password Management
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        config.salt + plain_password, hashed_password, scheme="bcrypt"
    )


def get_password_hash(password):
    return pwd_context.hash(config.salt + password)


def authenticate_user(db, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    # logger.warning(f"Queried User: {user.to_string()}")
    if not user:
        logger.error("Incorrect Email")
        return False
    if not verify_password(password, user.hashed_password):
        logger.error(
            f"Incorrect Password: {verify_password(password, user.hashed_password)}"
        )
        return False
    return user
