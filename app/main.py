from fastapi import FastAPI
from database import engine, Base
from routers import categories, suppliers, products, users, customers, sales, sale_items, payments, receipts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="POS APPLICATION", version="1.0")

app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(sale_items.router, prefix="/sale-items", tags=["Sale Items"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
