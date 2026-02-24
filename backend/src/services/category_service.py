from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.dao.category_dao import CategoryDAO
from src.dao.post_dao import PostDAO
from src.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    def list_categories(db: Session):
        return CategoryDAO.get_all(db)

    @staticmethod
    def get_category(db: Session, category_id: UUID):
        category = CategoryDAO.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return category

    @staticmethod
    def create_category(db: Session, payload: CategoryCreate):
        if CategoryDAO.get_by_name(db, payload.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )
        return CategoryDAO.create(db, name=payload.name)

    @staticmethod
    def update_category(db: Session, category_id: UUID, payload: CategoryUpdate):
        category = CategoryDAO.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        existing = CategoryDAO.get_by_name(db, payload.name)
        if existing and existing.id != category.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

        post_count = PostDAO.count_by_category(db, category_id)
        updated = CategoryDAO.update(db, category, name=payload.name)

        result = {
            "category": updated,
            "warning": None,
        }
        if post_count > 0:
            result["warning"] = (
                f"This category has been renamed. {post_count} post(s) are associated with it."
            )
        return result

    @staticmethod
    def delete_category(db: Session, category_id: UUID):
        category = CategoryDAO.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        post_count = PostDAO.count_by_category(db, category_id)
        if post_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete: {post_count} post(s) still use this category. "
                "Remove the category from those posts first, or reassign them.",
            )

        CategoryDAO.delete(db, category)
