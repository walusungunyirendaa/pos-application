from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from dependencies import require_admin
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryCreate, CategoryResponse

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    return repo.create(category.model_dump())


@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    return repo.get_all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    db_category = repo.get_by_id(category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(require_admin)])
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    db_category = repo.get_by_id(category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return repo.update(db_category, category.model_dump())


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    db_category = repo.get_by_id(category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    repo.delete(db_category)
    return None