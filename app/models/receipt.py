from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), nullable=False, unique=True)
    issued_date = Column(DateTime, nullable=False, server_default=func.now())
    file_url = Column(String(255), nullable=True)

    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False, unique=True)

    sale = relationship("Sale", back_populates="receipt")