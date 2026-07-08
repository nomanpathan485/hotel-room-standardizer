from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Room
from app.schemes import RoomCreate, RoomResponse

router = APIRouter()
@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail=f"Room with id {room_id} not found")
    return room

@router.post("/rooms", response_model=RoomResponse)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    new_room = Room(
        supplier_code=room.supplier_code,
        supplier_name=room.supplier_name,
        supplier_room_name=room.supplier_room_name,
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room