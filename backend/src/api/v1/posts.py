from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.dependencies import get_db, get_current_user
from src.models.user import User
from src.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
)
from src.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostListResponse)
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None, description="Filter by status: public, draft"),
    tag: str | None = Query(None, description="Filter by tag"),
    author_id: UUID | None = Query(None, description="Filter by author"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts, total = PostService.list_posts(
        db,
        current_user,
        page=page,
        page_size=page_size,
        status_filter=status,
        tag=tag,
        author_id=author_id,
    )
    return PostListResponse(items=posts, total=total, page=page, page_size=page_size)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PostService.get_post(db, post_id, current_user)


@router.post("", response_model=PostResponse, status_code=201)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PostService.create_post(db, current_user, payload)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: UUID,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PostService.update_post(db, post_id, current_user, payload)


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    PostService.delete_post(db, post_id, current_user)
