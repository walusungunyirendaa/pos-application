from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.payment import Payment
from models.sale import Sale
from schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    db_sale = db.query(Sale).filter(Sale.sale_id == payment.sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale does not exist")
    db_payment = Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/", response_model=List[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return db_payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, payment: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    db_sale = db.query(Sale).filter(Sale.sale_id == payment.sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale does not exist")
    for key, value in payment.model_dump().items():
        setattr(db_payment, key, value)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    db.delete(db_payment)
    db.commit()
    return None