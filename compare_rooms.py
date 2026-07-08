from rapidfuzz import fuzz
from app.database import SessionLocal
from app.models import Room

db = SessionLocal()

try:
    rooms = db.query(Room).all()

    for room in rooms:
        best_score = 0
        best_match = None

        for candidate in rooms:
            # Don't compare a room with itself
            if room.id == candidate.id:
                continue

            score = fuzz.token_set_ratio(
                room.supplier_room_name,
                candidate.supplier_room_name
            )

            if score > best_score:
                best_score = score
                best_match = candidate

        print("-" * 60)
        print(f"Room       : {room.supplier_room_name}")

        if best_match:
            print(f"Best Match : {best_match.supplier_room_name}")
            print(f"Score      : {best_score}")

finally:
    db.close()