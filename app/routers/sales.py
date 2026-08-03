from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.sale import Sale
from models.customer import Customer
from models.user import User
from schemas.sale import SaleCreate, SaleResponse

router = APIRouter()


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    if sale.customer_id:
        db_customer = db.query(Customer).filter(Customer.customer_id == sale.customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer does not exist")
    db_user = db.query(User).filter(User.user_id == sale.user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    db_sale = Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=List[SaleResponse])
def get_sales(db: Session = Depends(get_db)):
    return db.query(Sale).all()


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return db_sale


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(sale_id: int, sale: SaleCreate, db: Session = Depends(get_db)):
    db_sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    if sale.customer_id:
        db_customer = db.query(Customer).filter(Customer.customer_id == sale.customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer does not exist")
    db_user = db.query(User).filter(User.user_id == sale.user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    for key, value in sale.model_dump().items():
        setattr(db_sale, key, value)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    db.delete(db_sale)
    db.commit()
    return None
