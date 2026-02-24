import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.core.const import PostStatus
from src.db.base_class import Base

post_categories = Table(
    "post_categories",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    status = Column(
        SAEnum(*PostStatus, name="post_status_enum"),
        default=PostStatus.DRAFT,
        server_default=PostStatus.DRAFT,
        nullable=False,
    )
    tags = Column(ARRAY(String), default=list)
    author_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    author = relationship("User", back_populates="posts")
    categories = relationship(
        "Category", secondary=post_categories, back_populates="posts"
    )
