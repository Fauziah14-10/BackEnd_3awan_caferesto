from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base

class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True, index=True)
    name_customer = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(name={self.name_customer}, email={self.email})>"
    
    
