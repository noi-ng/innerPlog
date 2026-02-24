import uuid

from sqlalchemy import Column, String, Date, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.core.const import AccountStatus, UserRole
from src.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    fullname = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    account_status = Column(
        SAEnum(*AccountStatus, name="account_status_enum"),
        default=AccountStatus.ACTIVE,
        server_default=AccountStatus.ACTIVE,
        nullable=False,
    )
    role = Column(
        SAEnum(*UserRole, name="role_enum"),
        default=UserRole.WRITER,
        server_default=UserRole.WRITER,
        nullable=False,
    )

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
