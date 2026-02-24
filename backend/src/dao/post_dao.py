from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.core.const import PostStatus
from src.models.post import Post


class PostDAO:
    @staticmethod
    def get_by_id(db: Session, post_id: str | UUID) -> Post | None:
        return (
            db.query(Post)
            .options(joinedload(Post.author), joinedload(Post.categories))
            .filter(Post.id == post_id)
            .first()
        )

    @staticmethod
    def get_public_and_own(
        db: Session,
        current_user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 10,
        status_filter: str | None = None,
        tag_filter: str | None = None,
        author_id: UUID | None = None,
    ) -> tuple[list[Post], int]:
        """Return posts visible to a normal user: all their own + others' public posts."""
        query = db.query(Post).options(
            joinedload(Post.author), joinedload(Post.categories)
        )

        if author_id:
            if author_id == current_user_id:
                query = query.filter(Post.author_id == author_id)
            else:
                query = query.filter(
                    Post.author_id == author_id, Post.status == PostStatus.PUBLIC
                )
        else:
            query = query.filter(
                or_(
                    Post.author_id == current_user_id,
                    Post.status == PostStatus.PUBLIC,
                )
            )

        if status_filter:
            query = query.filter(Post.status == status_filter)
        if tag_filter:
            query = query.filter(Post.tags.any(tag_filter))

        total = query.count()
        posts = (
            query.order_by(Post.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return posts, total

    @staticmethod
    def get_all(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 10,
        status_filter: str | None = None,
    ) -> tuple[list[Post], int]:
        """Admin: return all posts regardless of ownership/status."""
        query = db.query(Post).options(
            joinedload(Post.author), joinedload(Post.categories)
        )
        if status_filter:
            query = query.filter(Post.status == status_filter)

        total = query.count()
        posts = (
            query.order_by(Post.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return posts, total

    @staticmethod
    def create(db: Session, **kwargs) -> Post:
        categories = kwargs.pop("categories", [])
        post = Post(**kwargs)
        post.categories = categories
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def update(db: Session, post: Post, **kwargs) -> Post:
        categories = kwargs.pop("categories", None)
        for key, value in kwargs.items():
            if value is not None:
                setattr(post, key, value)
        if categories is not None:
            post.categories = categories
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def delete(db: Session, post: Post) -> None:
        db.delete(post)
        db.commit()

    @staticmethod
    def count_by_category(db: Session, category_id: UUID) -> int:
        return (
            db.query(Post)
            .filter(Post.categories.any(id=category_id))
            .count()
        )
