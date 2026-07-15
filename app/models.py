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
    code = Column(String, nullable=True)
    provider_hotel_id = Column(String, nullable=True)
    board_basis = Column(String, nullable=True)
    beds = Column(String, nullable=True)
    room_description = Column(String, nullable=True)

    
