from sqlalchemy.orm import Session
from models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int):
        return self.db.query(Product).filter(Product.product_id == product_id).first()

    def get_all(self):
        return self.db.query(Product).all()

    def get_by_category(self, category_id: int):
        return self.db.query(Product).filter(Product.category_id == category_id).all()

    def get_by_supplier(self, supplier_id: int):
        return self.db.query(Product).filter(Product.supplier_id == supplier_id).all()

    def get_low_stock(self):
        return self.db.query(Product).filter(
            Product.quantity_in_stock <= Product.reorder_level
        ).all()

    def create(self, product_data: dict):
        db_product = Product(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, db_product: Product, updates: dict):
        for key, value in updates.items():
            setattr(db_product, key, value)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete(self, db_product: Product):
        self.db.delete(db_product)
        self.db.commit()