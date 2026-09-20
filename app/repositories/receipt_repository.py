from sqlalchemy.orm import Session
from models.receipt import Receipt


class ReceiptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, receipt_id: int):
        return self.db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()

    def get_all(self):
        return self.db.query(Receipt).all()

    def get_by_sale(self, sale_id: int):
        return self.db.query(Receipt).filter(Receipt.sale_id == sale_id).first()

    def get_by_receipt_number(self, receipt_number: str):
        return self.db.query(Receipt).filter(Receipt.receipt_number == receipt_number).first()

    def create(self, receipt_data: dict):
        db_receipt = Receipt(**receipt_data)
        self.db.add(db_receipt)
        self.db.commit()
        self.db.refresh(db_receipt)
        return db_receipt

    def update(self, db_receipt: Receipt, updates: dict):
        for key, value in updates.items():
            setattr(db_receipt, key, value)
        self.db.commit()
        self.db.refresh(db_receipt)
        return db_receipt

    def delete(self, db_receipt: Receipt):
        self.db.delete(db_receipt)
        self.db.commit()