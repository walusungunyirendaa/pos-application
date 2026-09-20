from sqlalchemy.orm import Session
from models.sale_item import SaleItem


class SaleItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_item_id: int):
        return self.db.query(SaleItem).filter(SaleItem.sale_item_id == sale_item_id).first()

    def get_all(self):
        return self.db.query(SaleItem).all()

    def get_by_sale(self, sale_id: int):
        return self.db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()

    def get_by_product(self, product_id: int):
        return self.db.query(SaleItem).filter(SaleItem.product_id == product_id).all()

    def create(self, sale_item_data: dict):
        db_sale_item = SaleItem(**sale_item_data)
        self.db.add(db_sale_item)
        self.db.commit()
        self.db.refresh(db_sale_item)
        return db_sale_item

    def update(self, db_sale_item: SaleItem, updates: dict):
        for key, value in updates.items():
            setattr(db_sale_item, key, value)
        self.db.commit()
        self.db.refresh(db_sale_item)
        return db_sale_item

    def delete(self, db_sale_item: SaleItem):
        self.db.delete(db_sale_item)
        self.db.commit()