import string

from sqlalchemy import Column, Integer, String
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(Integer)
    supplier_name = Column(String)
    supplier_room_name = Column(String)
    standard_room_name = Column(String, nullable=True)  # This field can be null initially

    
