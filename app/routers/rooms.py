from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Room
from app.schemes import RoomCreate, RoomResponse
from app.services.grouping_engine import group_rooms
from app.services.response_formatter import format_grouped_response
from app.services.group_comparator import compare_group_outputs

router = APIRouter()
@router.get("/rooms", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()

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

@router.put("/rooms/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, room: RoomCreate, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()

    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    db_room.supplier_code = room.supplier_code
    db_room.supplier_name = room.supplier_name
    db_room.supplier_room_name = room.supplier_room_name

    db.commit()
    db.refresh(db_room)

    return db_room

@router.delete("/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()

    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    db.delete(db_room)
    db.commit()

    return {"message": "Room deleted successfully"}

def save_room_mapping(db: Session, groups: list[dict]) -> None:
    for group in groups:
        standard_room_name =group["standard_room_name"]
        for grouped_room in group["rooms"]:
            room = (
                db.query(Room)
                .filter(Room.id == grouped_room["id"])
                .first()
            )

            if room:
                room.standard_room_name = standard_room_name
    db.commit()



@router.post("/group-rooms")
def group_rooms_api(
    generate_standard_name: bool = False,
    db: Session = Depends(get_db),
    
):
    rooms = db.query(Room).all()

    room_data = [
    {
        "id": room.id,
        "supplier": room.supplier_name,
        "room_name": room.supplier_room_name,
        "standard_room_name": room.standard_room_name,

        "code": room.code,
        "provider_hotel_id": room.provider_hotel_id,
        "board_basis": room.board_basis,
        "beds": room.beds,
        "room_description": room.room_description,
    }
    for room in rooms
]

    groups = group_rooms(
        room_data,
        generate_standard_name=generate_standard_name,
    )

    if generate_standard_name:
        save_room_mapping(db, groups)

    return format_grouped_response(groups)

@router.get("/room-names")
def get_room_names(db: Session = Depends(get_db)):
    rows = (
        db.query(Room.supplier_room_name)
        .distinct()
        .order_by(Room.supplier_room_name)
        .all()
    )

@router.post("/group-rooms-direct")
def group_rooms_direct(payload: dict):
    room_rates = payload.get("roomRates", [])

    room_data = [
        {
            **room,
            "id": room.get("index"),
            "supplier": room.get("provider"),
            "room_name": room.get("roomName", ""),
            "standard_room_name": None,
        }
        for room in room_rates
    ]

    groups = group_rooms(
        room_data,
        generate_standard_name=False,
    )

    return format_grouped_response(groups)

@router.post("/compare-groups")
def compare_groups(payload: dict):
    vervotech_response = payload.get("vervotech_response", {})
    our_response = payload.get("our_response", {})

    return compare_group_outputs(
        vervotech_response,
        our_response,
    )