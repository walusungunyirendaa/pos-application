from sqlalchemy.orm import Session
from repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_product(self, product_id: int):
        return self.repo.get_by_id(product_id)

    def list_products(self):
        return self.repo.get_all()

    def get_low_stock_products(self):
        return self.repo.get_low_stock()