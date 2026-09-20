from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from dependencies import require_manager
from repositories.product_repository import ProductRepository
from repositories.category_repository import CategoryRepository
from repositories.supplier_repository import SupplierRepository
from schemas.product import ProductCreate, ProductResponse

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    category_repo = CategoryRepository(db)
    if not category_repo.get_by_id(product.category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")
    if product.supplier_id is not None and not SupplierRepository(db).get_by_id(product.supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier does not exist")
    repo = ProductRepository(db)
    return repo.create(product.model_dump())


@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.get_all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    db_product = repo.get_by_id(product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return db_product


@router.put("/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_manager)])
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    db_product = repo.get_by_id(product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.category_id:
        category_repo = CategoryRepository(db)
        if not category_repo.get_by_id(product.category_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")
    if product.supplier_id is not None and not SupplierRepository(db).get_by_id(product.supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier does not exist")
    return repo.update(db_product, product.model_dump())


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_manager)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    db_product = repo.get_by_id(product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    repo.delete(db_product)
    return None