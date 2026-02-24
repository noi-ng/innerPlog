import re
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.core.const import AccountStatus

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


def _validate_email(value: str) -> str:
    if not EMAIL_REGEX.fullmatch(value):
        raise ValueError("Invalid email format")
    return value.lower().strip()


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    fullname: str | None = Field(default=None, max_length=100)
    dob: date | None = None
    description: str | None = Field(default=None, max_length=500)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_]+", v):
            raise ValueError(
                "Username must contain only letters, digits, and underscores"
            )
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        return _validate_email(v)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("dob")
    @classmethod
    def dob_in_past(cls, v: date | None) -> date | None:
        if v is not None and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @field_validator("fullname")
    @classmethod
    def fullname_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Fullname cannot be blank")
        return v.strip() if v else v


class UserUpdate(BaseModel):
    fullname: str | None = Field(default=None, max_length=100)
    dob: date | None = None
    description: str | None = Field(default=None, max_length=500)
    email: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str | None) -> str | None:
        if v is not None:
            return _validate_email(v)
        return v

    @field_validator("dob")
    @classmethod
    def dob_in_past(cls, v: date | None) -> date | None:
        if v is not None and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @field_validator("fullname")
    @classmethod
    def fullname_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Fullname cannot be blank")
        return v.strip() if v else v


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    fullname: str | None = None
    dob: date | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    account_status: str
    role: str

    model_config = {"from_attributes": True}


class AdminUserUpdate(BaseModel):
    account_status: AccountStatus
