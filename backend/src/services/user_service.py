from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.dao.user_dao import UserDAO
from src.schemas.user import UserUpdate, AdminUserUpdate


class UserService:
    @staticmethod
    def get_current_user_profile(db: Session, user):
        return user

    @staticmethod
    def update_profile(db: Session, user, payload: UserUpdate):
        if payload.email and payload.email != user.email:
            existing = UserDAO.get_by_email(db, payload.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use",
                )

        return UserDAO.update(
            db,
            user,
            fullname=payload.fullname,
            dob=payload.dob,
            description=payload.description,
            email=payload.email,
        )

    @staticmethod
    def admin_get_all_users(db: Session, skip: int = 0, limit: int = 50):
        return UserDAO.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def admin_update_user_status(
        db: Session, user_id: UUID, payload: AdminUserUpdate
    ):
        user = UserDAO.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserDAO.update(db, user, account_status=payload.account_status)
