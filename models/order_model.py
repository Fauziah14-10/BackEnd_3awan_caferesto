from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "order"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    total_price = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    order_date = Column(DateTime, default=datetime.utcnow)

    # Relasi ke customer
    customer = relationship("Customer", back_populates="orders")

    # Items for this order (previously Cart was used) — now normalized into OrderItem
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(order_id={self.order_id}, customer_id={self.customer_id}, total_price={self.total_price})>"
