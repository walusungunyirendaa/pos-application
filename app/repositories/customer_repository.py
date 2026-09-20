from sqlalchemy.orm import Session
from models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: int):
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()

    def get_all(self):
        return self.db.query(Customer).all()

    def create(self, customer_data: dict):
        db_customer = Customer(**customer_data)
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def update(self, db_customer: Customer, updates: dict):
        for key, value in updates.items():
            setattr(db_customer, key, value)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def delete(self, db_customer: Customer):
        self.db.delete(db_customer)
        self.db.commit()

    def add_loyalty_points(self, customer_id: int, points: int):
        db_customer = self.get_by_id(customer_id)
        if db_customer:
            db_customer.loyalty_points = (db_customer.loyalty_points or 0) + points
            self.db.commit()
            self.db.refresh(db_customer)
        return db_customer