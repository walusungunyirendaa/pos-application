from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.sale_item import SaleItem
from models.sale import Sale
from models.product import Product
from schemas.sale_item import SaleItemCreate, SaleItemResponse

router = APIRouter()


@router.post("/", response_model=SaleItemResponse, status_code=status.HTTP_201_CREATED)
def create_sale_item(sale_item: SaleItemCreate, db: Session = Depends(get_db)):
    db_sale = db.query(Sale).filter(Sale.sale_id == sale_item.sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale does not exist")
    db_product = db.query(Product).filter(Product.product_id == sale_item.product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product does not exist")
    db_sale_item = SaleItem(**sale_item.model_dump())
    db.add(db_sale_item)
    db.commit()
    db.refresh(db_sale_item)
    return db_sale_item


@router.get("/", response_model=List[SaleItemResponse])
def get_sale_items(db: Session = Depends(get_db)):
    return db.query(SaleItem).all()


@router.get("/{sale_item_id}", response_model=SaleItemResponse)
def get_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    db_sale_item = db.query(SaleItem).filter(SaleItem.sale_item_id == sale_item_id).first()
    if not db_sale_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale item not found")
    return db_sale_item


@router.put("/{sale_item_id}", response_model=SaleItemResponse)
def update_sale_item(sale_item_id: int, sale_item: SaleItemCreate, db: Session = Depends(get_db)):
    db_sale_item = db.query(SaleItem).filter(SaleItem.sale_item_id == sale_item_id).first()
    if not db_sale_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale item not found")
    db_sale = db.query(Sale).filter(Sale.sale_id == sale_item.sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale does not exist")
    db_product = db.query(Product).filter(Product.product_id == sale_item.product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product does not exist")
    for key, value in sale_item.model_dump().items():
        setattr(db_sale_item, key, value)
    db.commit()
    db.refresh(db_sale_item)
    return db_sale_item


@router.delete("/{sale_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    db_sale_item = db.query(SaleItem).filter(SaleItem.sale_item_id == sale_item_id).first()
    if not db_sale_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale item not found")
    db.delete(db_sale_item)
    db.commit()
    return None
