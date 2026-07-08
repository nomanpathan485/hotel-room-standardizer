from app.database import SessionLocal
from app.models import Room

db = SessionLocal()

rooms = db.query(Room).all()

print(f"Total rooms: {len(rooms)}")

for room in rooms:
    print(room.supplier_room_name)

db.close()