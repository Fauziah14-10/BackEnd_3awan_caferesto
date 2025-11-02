from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class OrderItem(Base):
    __tablename__ = "order_item"

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("order.order_id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("menu.id_menu"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # relationships
    order = relationship("Order", back_populates="order_items")
    menu = relationship("Menu")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, menu_id={self.menu_id}, qty={self.quantity})>"
