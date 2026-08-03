from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.receipt import Receipt
from models.sale import Sale
from schemas.receipt import ReceiptCreate, ReceiptResponse

router = APIRouter()


@router.post("/", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_receipt(receipt: ReceiptCreate, db: Session = Depends(get_db)):
    db_sale = db.query(Sale).filter(Sale.sale_id == receipt.sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale does not exist")
    existing_receipt = db.query(Receipt).filter(Receipt.sale_id == receipt.sale_id).first()
    if existing_receipt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receipt already exists for this sale")
    db_receipt = Receipt(**receipt.model_dump())
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt


@router.get("/", response_model=List[ReceiptResponse])
def get_receipts(db: Session = Depends(get_db)):
    return db.query(Receipt).all()


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    db_receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not db_receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    return db_receipt


@router.put("/{receipt_id}", response_model=ReceiptResponse)
def update_receipt(receipt_id: int, receipt: ReceiptCreate, db: Session = Depends(get_db)):
    db_receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not db_receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    db_sale = db.query(Sale).filter(Sale.sale_id == receipt.sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale does not exist")
    if receipt.sale_id != db_receipt.sale_id:
        existing_receipt = db.query(Receipt).filter(Receipt.sale_id == receipt.sale_id).first()
        if existing_receipt:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receipt already exists for this sale")
    for key, value in receipt.model_dump().items():
        setattr(db_receipt, key, value)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    db_receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not db_receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    db.delete(db_receipt)
    db.commit()
    return None
