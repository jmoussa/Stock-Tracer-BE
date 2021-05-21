from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from stock_tracer.database.database import get_db
from stock_tracer.database import schemas, models, crud
from stock_tracer.authentication.auth import (
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
    authenticate_user,
    create_access_token,
)

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/verify", response_model=schemas.User)
def validate_current_user(current_user: models.User = Depends(get_current_active_user)):
    user = schemas.User(**current_user.to_dict())
    return user


@router.post("/register", response_model=Token)
def register_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_create = {
        "email": form_data.username,
        "password": form_data.password,
        "financial_profile": {},
    }
    user = crud.create_user(db, schemas.UserCreate(**user_create))
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}
