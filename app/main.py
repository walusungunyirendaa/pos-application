from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from config import settings
from database import engine, Base
from routers import categories, suppliers, products, users, customers, sales, sale_items, payments, receipts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="POS APPLICATION", version="1.0")


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Conflict: duplicate value or record is referenced by other data"},
    )


app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["Categories"])
app.include_router(suppliers.router, prefix=f"{settings.API_V1_STR}/suppliers", tags=["Suppliers"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["Products"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(customers.router, prefix=f"{settings.API_V1_STR}/customers", tags=["Customers"])
app.include_router(sales.router, prefix=f"{settings.API_V1_STR}/sales", tags=["Sales"])
app.include_router(sale_items.router, prefix=f"{settings.API_V1_STR}/sale-items", tags=["Sale Items"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["Payments"])
app.include_router(receipts.router, prefix=f"{settings.API_V1_STR}/receipts", tags=["Receipts"])

@app.get("/")
def root():
    return {"message": "Retail POS System API", "status": "running"}