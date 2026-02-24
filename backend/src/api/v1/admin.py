from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.dependencies import get_db, get_current_admin
from src.schemas.user import UserResponse, AdminUserUpdate
from src.schemas.post import PostResponse, PostListResponse, AdminPostUpdate
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.services.user_service import UserService
from src.services.post_service import PostService
from src.services.category_service import CategoryService

router = APIRouter(prefix="/admin", tags=["admin"])


# --- User management ---


@router.get("/users", response_model=list[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return UserService.admin_get_all_users(db, skip=skip, limit=limit)


@router.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: UUID,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return UserService.admin_update_user_status(db, user_id, payload)


# --- Post management ---


@router.get("/posts", response_model=PostListResponse)
def list_all_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    posts, total = PostService.admin_list_all_posts(
        db, page=page, page_size=page_size, status_filter=status
    )
    return PostListResponse(items=posts, total=total, page=page, page_size=page_size)


@router.patch("/posts/{post_id}/status", response_model=PostResponse)
def update_post_status(
    post_id: UUID,
    payload: AdminPostUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return PostService.admin_update_post_status(db, post_id, payload)


# --- Category management ---


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return CategoryService.list_categories(db)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return CategoryService.create_category(db, payload)


@router.put("/categories/{category_id}")
def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = CategoryService.update_category(db, category_id, payload)
    return {
        "category": CategoryResponse.model_validate(result["category"]),
        "warning": result["warning"],
    }


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    CategoryService.delete_category(db, category_id)
