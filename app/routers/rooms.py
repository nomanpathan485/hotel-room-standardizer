from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime
from app.models import Room
from fastapi import HTTPException
from app.services.dataset_store import save_benchmark_case
from app.schemes import RoomCreate, RoomResponse
from app.services.response_formatter import format_grouped_response
from app.services.group_comparator import (
    compare_group_outputs,
    diagnose_false_splits,
    diagnose_wrong_merges,
)
from app.services.grouping_engine import (
    group_rooms,
    group_rooms_v2,
    group_rooms_v3,
    group_rooms_v4
)
from app.services.rateloc_client import fetch_rooms_from_rateloc
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
    input_data = payload.get("input_data", {})
    vervotech_response = payload.get("vervotech_response", {})
    our_response = payload.get("our_response", {})

    comparison = compare_group_outputs(
        vervotech_response,
        our_response,
    )

    false_split_diagnostics = diagnose_false_splits(
        input_data,
        vervotech_response,
    )

    wrong_merge_diagnostics = diagnose_wrong_merges(
        input_data,
        vervotech_response,
        our_response,
    )

    return {
        "comparison": comparison,
        "false_split_diagnostics": false_split_diagnostics,
        "wrong_merge_diagnostics": wrong_merge_diagnostics,
    }
@router.post("/group-rooms-direct-v2")
def group_rooms_direct_v2(payload: dict):
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

    groups = group_rooms_v2(
        room_data,
        generate_standard_name=False,
    )

    return format_grouped_response(groups)

@router.post("/group-rooms-direct-v3")
def group_rooms_direct_v3(payload: dict):
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

    groups = group_rooms_v3(
        room_data,
        generate_standard_name=False,
    )

    return format_grouped_response(groups)

@router.post("/group-rooms-direct-v4")
def group_rooms_direct_v4(payload: dict):
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

    groups = group_rooms_v4(
        room_data,
        generate_standard_name=False,
    )

    return format_grouped_response(groups)

@router.post("/fetch-live-rooms")
async def fetch_live_rooms(payload: dict):
    response = await fetch_rooms_from_rateloc(payload)

    return response

@router.post("/save-benchmark")
async def save_benchmark(payload: dict):
    # 1. Get the original hotel input and Vervotech result
    input_data = payload.get("input_data")
    vervotech_response = payload.get("vervotech_response")

    # 2. Validate input data
    if not input_data:
        raise HTTPException(
            status_code=400,
            detail="input_data is required.",
        )

    # 3. Validate Vervotech response
    if not vervotech_response:
        raise HTTPException(
            status_code=400,
            detail="vervotech_response is required.",
        )

    # 4. Get the hotel ID automatically from the input data
    vervotech_hotel_id = input_data.get("vervotechHotelId")

    if not vervotech_hotel_id:
        raise HTTPException(
            status_code=400,
            detail="vervotechHotelId is required inside input_data.",
        )

    # 5. Generate a unique benchmark case ID automatically
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    case_id = f"hotel_{vervotech_hotel_id}_{timestamp}"

    # 6. Extract room rates
    room_rates = input_data.get("roomRates", [])

    if not room_rates:
        raise HTTPException(
            status_code=400,
            detail="No roomRates found inside input_data.",
        )

    # 7. Convert the external room format
    # into the format expected by our grouping engine
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

    # 8. Run our V4 grouping engine
    groups = group_rooms_v4(
        room_data,
        generate_standard_name=False,
    )

    # 9. Convert V4 groups into our final response format
    our_response = format_grouped_response(groups)

    # 10. Save all three benchmark artifacts
    saved_files = save_benchmark_case(
        case_id=case_id,
        input_data=input_data,
        vervotech_response=vervotech_response,
        our_response=our_response,
    )

    # 11. Return confirmation to Postman
    return {
        "message": "Benchmark saved successfully.",
        "case_id": case_id,
        "vervotech_hotel_id": vervotech_hotel_id,
        "saved_files": {
            name: str(path)
            for name, path in saved_files.items()
        },
    }