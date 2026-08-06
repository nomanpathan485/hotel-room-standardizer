from datetime import datetime
from app.services.feature_extractor import get_identity_tokens

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Room
from app.schemes import RoomCreate, RoomResponse
from app.services.dataset_store import save_benchmark_case
from app.services.group_comparator import (
    compare_group_outputs,
    diagnose_false_splits,
    diagnose_wrong_merges,
)
from app.services.grouping_engine import group_rooms_ml
from app.services.rateloc_client import fetch_rooms_from_rateloc
from app.services.response_formatter import format_grouped_response


router = APIRouter()


def convert_external_rooms(
    room_rates: list[dict],
) -> list[dict]:
    """
    Convert the external supplier format into the internal
    format expected by the grouping engine.
    """
    return [
        {
            **room,
            "id": room.get("index"),
            "supplier": room.get("provider"),
            "room_name": room.get("roomName", ""),
            "standard_room_name": None,
        }
        for room in room_rates
    ]


def save_room_mapping(
    db: Session,
    groups: list[dict],
) -> None:
    """
    Save the generated canonical room name back to each
    database room.

    group_id is intentionally not saved because it only
    exists for the current grouping operation.
    """
    for group in groups:
        standard_room_name = group["standard_room_name"]

        for grouped_room in group["rooms"]:
            room = (
                db.query(Room)
                .filter(Room.id == grouped_room["id"])
                .first()
            )

            if room is not None:
                room.standard_room_name = standard_room_name

    db.commit()


@router.get(
    "/rooms",
    response_model=list[RoomResponse],
)
def get_rooms(
    db: Session = Depends(get_db),
):
    return db.query(Room).all()


@router.get(
    "/rooms/{room_id}",
    response_model=RoomResponse,
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
):
    room = (
        db.query(Room)
        .filter(Room.id == room_id)
        .first()
    )

    if room is None:
        raise HTTPException(
            status_code=404,
            detail=f"Room with id {room_id} not found",
        )

    return room


@router.post(
    "/rooms",
    response_model=RoomResponse,
)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
):
    new_room = Room(
        supplier_code=room.supplier_code,
        supplier_name=room.supplier_name,
        supplier_room_name=room.supplier_room_name,
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


@router.put(
    "/rooms/{room_id}",
    response_model=RoomResponse,
)
def update_room(
    room_id: int,
    room: RoomCreate,
    db: Session = Depends(get_db),
):
    db_room = (
        db.query(Room)
        .filter(Room.id == room_id)
        .first()
    )

    if db_room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    db_room.supplier_code = room.supplier_code
    db_room.supplier_name = room.supplier_name
    db_room.supplier_room_name = room.supplier_room_name

    db.commit()
    db.refresh(db_room)

    return db_room


@router.delete("/rooms/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
):
    db_room = (
        db.query(Room)
        .filter(Room.id == room_id)
        .first()
    )

    if db_room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    db.delete(db_room)
    db.commit()

    return {
        "message": "Room deleted successfully",
    }


@router.get("/room-names")
def get_room_names(
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Room.supplier_room_name)
        .distinct()
        .order_by(Room.supplier_room_name)
        .all()
    )

    return [
        row[0]
        for row in rows
    ]


@router.post("/group-rooms")
def group_rooms_api(
    generate_standard_name: bool = False,
    db: Session = Depends(get_db),
):
    """
    Group rooms already stored in the database using the
    active HGB matching pipeline.
    """
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

    groups = group_rooms_ml(
        room_data,
        generate_standard_name=generate_standard_name,
    )

    if generate_standard_name:
        save_room_mapping(
            db,
            groups,
        )

    return format_grouped_response(groups)


@router.post("/group-rooms-direct")
@router.post("/group-rooms-direct-ml")
def group_rooms_direct(
    payload: dict,
):
    """
    Group rooms supplied directly in the request without
    first saving them to the database.

    The second route is temporarily retained as an alias
    for existing Postman requests.
    """
    room_rates = payload.get("roomRates", [])

    if not room_rates:
        raise HTTPException(
            status_code=400,
            detail="roomRates is required and cannot be empty.",
        )

    room_data = convert_external_rooms(room_rates)

    groups = group_rooms_ml(
        room_data,
        generate_standard_name=False,
    )

    return format_grouped_response(groups)


@router.post("/compare-groups")
def compare_groups(payload: dict):
    input_data = payload.get("input_data", {})
    vervotech_response = payload.get(
        "vervotech_response",
        {},
    )
    our_response = payload.get(
        "our_response",
        {},
    )

    comparison = compare_group_outputs(
        vervotech_response,
        our_response,
    )

    false_split_diagnostics = diagnose_false_splits(
        input_data,
        vervotech_response,
        our_response,
    )

    wrong_merge_diagnostics = diagnose_wrong_merges(
        input_data,
        vervotech_response,
        our_response,
    )

    # Diagnostic-only inspection of possible named-room identity words.
    # This does not affect grouping or matching yet.
    identity_token_diagnostics = {}

    for room in input_data.get("roomRates", []):
        room_name = room.get("roomName", "")
        identity_tokens = get_identity_tokens(room_name)

        for token in identity_tokens:
            identity_token_diagnostics.setdefault(
                token,
                [],
            ).append(
                {
                    "index": room.get("index"),
                    "room_name": room_name,
                }
            )

    return {
        "comparison": comparison,
        "false_split_diagnostics": (
            false_split_diagnostics
        ),
        "wrong_merge_diagnostics": (
            wrong_merge_diagnostics
        ),
        "identity_token_diagnostics": (
            identity_token_diagnostics
        ),
    }


@router.post("/fetch-live-rooms")
async def fetch_live_rooms(
    payload: dict,
):
    return await fetch_rooms_from_rateloc(payload)


@router.post("/save-benchmark")
async def save_benchmark(
    payload: dict,
):
    input_data = payload.get("input_data")
    vervotech_response = payload.get(
        "vervotech_response"
    )

    if not input_data:
        raise HTTPException(
            status_code=400,
            detail="input_data is required.",
        )

    if not vervotech_response:
        raise HTTPException(
            status_code=400,
            detail="vervotech_response is required.",
        )

    vervotech_hotel_id = input_data.get(
        "vervotechHotelId"
    )

    if not vervotech_hotel_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "vervotechHotelId is required "
                "inside input_data."
            ),
        )

    room_rates = input_data.get("roomRates", [])

    if not room_rates:
        raise HTTPException(
            status_code=400,
            detail=(
                "No roomRates found inside input_data."
            ),
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    case_id = (
        f"hotel_{vervotech_hotel_id}_{timestamp}"
    )

    room_data = convert_external_rooms(room_rates)

    # Benchmarks now evaluate the active HGB engine,
    # not the retired V4 rule-based matcher.
    groups = group_rooms_ml(
        room_data,
        generate_standard_name=False,
    )

    our_response = format_grouped_response(groups)

    saved_files = save_benchmark_case(
        case_id=case_id,
        input_data=input_data,
        vervotech_response=vervotech_response,
        our_response=our_response,
    )

    return {
        "message": "Benchmark saved successfully.",
        "case_id": case_id,
        "vervotech_hotel_id": vervotech_hotel_id,
        "saved_files": {
            name: str(path)
            for name, path in saved_files.items()
        },
    }