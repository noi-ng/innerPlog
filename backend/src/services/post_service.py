from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.const import PostStatus
from src.dao.post_dao import PostDAO
from src.dao.category_dao import CategoryDAO
from src.models.user import User
from src.schemas.post import PostCreate, PostUpdate, AdminPostUpdate


class PostService:
    @staticmethod
    def _resolve_categories(db: Session, category_ids: list[UUID]):
        categories = []
        for cid in category_ids:
            cat = CategoryDAO.get_by_id(db, cid)
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category {cid} not found",
                )
            categories.append(cat)
        return categories

    @staticmethod
    def list_posts(
        db: Session,
        current_user: User,
        *,
        page: int = 1,
        page_size: int = 10,
        status_filter: str | None = None,
        tag: str | None = None,
        author_id: UUID | None = None,
    ):
        posts, total = PostDAO.get_public_and_own(
            db,
            current_user.id,
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            tag_filter=tag,
            author_id=author_id,
        )
        return posts, total

    @staticmethod
    def get_post(db: Session, post_id: UUID, current_user: User):
        post = PostDAO.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        if post.status != PostStatus.PUBLIC and post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this post",
            )
        return post

    @staticmethod
    def create_post(db: Session, current_user: User, payload: PostCreate):
        categories = PostService._resolve_categories(db, payload.category_ids)

        post = PostDAO.create(
            db,
            title=payload.title,
            content=payload.content,
            status=payload.status,
            tags=payload.tags,
            author_id=current_user.id,
            categories=categories,
        )
        return PostDAO.get_by_id(db, post.id)

    @staticmethod
    def update_post(db: Session, post_id: UUID, current_user: User, payload: PostUpdate):
        post = PostDAO.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own posts",
            )
        update_kwargs: dict = {}
        if payload.title is not None:
            update_kwargs["title"] = payload.title
        if payload.content is not None:
            update_kwargs["content"] = payload.content
        if payload.status is not None:
            update_kwargs["status"] = payload.status
        if payload.tags is not None:
            update_kwargs["tags"] = payload.tags

        if payload.category_ids is not None:
            update_kwargs["categories"] = PostService._resolve_categories(
                db, payload.category_ids
            )

        post = PostDAO.update(db, post, **update_kwargs)
        return PostDAO.get_by_id(db, post.id)

    @staticmethod
    def delete_post(db: Session, post_id: UUID, current_user: User):
        post = PostDAO.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own posts",
            )
        PostDAO.delete(db, post)

    # --- Admin operations ---

    @staticmethod
    def admin_list_all_posts(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 10,
        status_filter: str | None = None,
    ):
        return PostDAO.get_all(
            db, page=page, page_size=page_size, status_filter=status_filter
        )

    @staticmethod
    def admin_update_post_status(db: Session, post_id: UUID, payload: AdminPostUpdate):
        post = PostDAO.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        return PostDAO.update(db, post, status=payload.status)
