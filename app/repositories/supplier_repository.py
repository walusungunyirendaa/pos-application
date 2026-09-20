from sqlalchemy.orm import Session
from models.supplier import Supplier


class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, supplier_id: int):
        return self.db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    def get_all(self):
        return self.db.query(Supplier).all()

    def create(self, supplier_data: dict):
        db_supplier = Supplier(**supplier_data)
        self.db.add(db_supplier)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier

    def update(self, db_supplier: Supplier, updates: dict):
        for key, value in updates.items():
            setattr(db_supplier, key, value)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier

    def delete(self, db_supplier: Supplier):
        self.db.delete(db_supplier)
        self.db.commit()