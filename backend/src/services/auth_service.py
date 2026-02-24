from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.const import AccountStatus
from src.core.security import hash_password, verify_password, create_access_token
from src.dao.user_dao import UserDAO
from src.schemas.user import UserCreate


class AuthService:
    @staticmethod
    def register(db: Session, payload: UserCreate):
        if UserDAO.get_by_username(db, payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        if UserDAO.get_by_email(db, payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = UserDAO.create(
            db,
            username=payload.username,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            fullname=payload.fullname,
            dob=payload.dob,
            description=payload.description,
        )
        return user

    @staticmethod
    def login(db: Session, username: str, password: str):
        user = UserDAO.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.account_status == AccountStatus.BANNED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been banned",
            )

        token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
