from sqlalchemy.orm import Session
from models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int):
        return self.db.query(Product).filter(Product.product_id == product_id).first()

    def get_all(self):
        return self.db.query(Product).all()