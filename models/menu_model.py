from sqlalchemy import Column, Integer, String
from config.database import Base

class Menu(Base):
    __tablename__ = "menu"

    id_menu = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    image_url = Column(String(255), nullable=False)
