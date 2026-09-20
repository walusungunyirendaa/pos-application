from sqlalchemy.orm import Session
from models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, payment_id: int):
        return self.db.query(Payment).filter(Payment.payment_id == payment_id).first()

    def get_all(self):
        return self.db.query(Payment).all()

    def get_by_sale(self, sale_id: int):
        return self.db.query(Payment).filter(Payment.sale_id == sale_id).all()

    def get_by_method(self, payment_method: str):
        return self.db.query(Payment).filter(Payment.payment_method == payment_method).all()

    def create(self, payment_data: dict):
        db_payment = Payment(**payment_data)
        self.db.add(db_payment)
        self.db.commit()
        self.db.refresh(db_payment)
        return db_payment

    def update(self, db_payment: Payment, updates: dict):
        for key, value in updates.items():
            setattr(db_payment, key, value)
        self.db.commit()
        self.db.refresh(db_payment)
        return db_payment

    def delete(self, db_payment: Payment):
        self.db.delete(db_payment)
        self.db.commit()