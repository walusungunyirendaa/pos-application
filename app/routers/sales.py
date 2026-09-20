from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from dependencies import require_cashier, require_manager
from repositories.sale_repository import SaleRepository
from repositories.customer_repository import CustomerRepository
from repositories.user_repository import UserRepository
from schemas.sale import SaleCreate, SaleResponse

router = APIRouter()


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_cashier)])
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    if sale.customer_id:
        customer_repo = CustomerRepository(db)
        if not customer_repo.get_by_id(sale.customer_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer does not exist")
    user_repo = UserRepository(db)
    if not user_repo.get_by_id(sale.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    repo = SaleRepository(db)
    return repo.create(sale.model_dump())


@router.get("/", response_model=List[SaleResponse])
def get_sales(db: Session = Depends(get_db)):
    repo = SaleRepository(db)
    return repo.get_all()


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    repo = SaleRepository(db)
    db_sale = repo.get_by_id(sale_id)
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return db_sale


@router.put("/{sale_id}", response_model=SaleResponse, dependencies=[Depends(require_cashier)])
def update_sale(sale_id: int, sale: SaleCreate, db: Session = Depends(get_db)):
    repo = SaleRepository(db)
    db_sale = repo.get_by_id(sale_id)
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    if sale.customer_id:
        customer_repo = CustomerRepository(db)
        if not customer_repo.get_by_id(sale.customer_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer does not exist")
    user_repo = UserRepository(db)
    if not user_repo.get_by_id(sale.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    return repo.update(db_sale, sale.model_dump())


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_manager)])
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    repo = SaleRepository(db)
    db_sale = repo.get_by_id(sale_id)
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    repo.delete(db_sale)
    return None