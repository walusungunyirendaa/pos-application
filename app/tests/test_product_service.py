from models.product import Product
from services.product_service import ProductService


def _add_product(db, category_id, sku, stock, reorder):
    product = Product(
        sku=sku, name=sku, price=1, quantity_in_stock=stock,
        reorder_level=reorder, category_id=category_id,
    )
    db.add(product)
    db.commit()
    return product


class TestProductService:
    def test_list_and_get(self, db_session, sample_product):
        service = ProductService(db_session)
        assert [p.sku for p in service.list_products()] == ["CC001"]
        assert service.get_product(sample_product["product_id"]).name == "Coca-Cola 500ml"

    def test_get_missing_product_returns_none(self, db_session):
        assert ProductService(db_session).get_product(9999) is None

    def test_low_stock_includes_items_at_or_below_reorder_level(self, db_session, sample_product):
        category_id = sample_product["category_id"]
        _add_product(db_session, category_id, "LOW", stock=5, reorder=20)
        _add_product(db_session, category_id, "EDGE", stock=20, reorder=20)
        _add_product(db_session, category_id, "NOLEVEL", stock=0, reorder=None)

        low = {p.sku for p in ProductService(db_session).get_low_stock_products()}

        assert low == {"LOW", "EDGE"}  
