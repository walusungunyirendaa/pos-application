from sqlalchemy.orm import Session
from models.sale import Sale
from models.sale_item import SaleItem


class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_id: int):
        return self.db.query(Sale).filter(Sale.sale_id == sale_id).first()

    def get_all(self):
        return self.db.query(Sale).all()

    def get_by_customer(self, customer_id: int):
        return self.db.query(Sale).filter(Sale.customer_id == customer_id).all()

    def get_by_user(self, user_id: int):
        return self.db.query(Sale).filter(Sale.user_id == user_id).all()

    def create(self, sale_data: dict):
        db_sale = Sale(**sale_data)
        self.db.add(db_sale)
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale

    def update(self, db_sale: Sale, updates: dict):
        for key, value in updates.items():
            setattr(db_sale, key, value)
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale

    def delete(self, db_sale: Sale):
        self.db.delete(db_sale)
        self.db.commit()

    def add_item(self, item_data: dict):
        db_item = SaleItem(**item_data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item