from repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, db):
        self.repo = ProductRepository(db)

    def get_product(self, product_id: int):
        return self.repo.get_by_id(product_id)