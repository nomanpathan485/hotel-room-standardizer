import json

from app.database import SessionLocal
from app.models import Room


def import_rooms():
    db = SessionLocal()

    try:
        # Open the JSON file
        with open("data/rooms.json", "r", encoding="utf-8") as file:
            rooms = json.load(file)

        print(type(rooms))
        print(len(rooms))

        # Insert each room into the database
        for room in rooms:
            new_room = Room(
                supplier_code=int(room["supplierCode"]),
                supplier_name=room["supplierName"],
                supplier_room_name=room["roomName"]
            )

            db.add(new_room)

        # Save all changes
        db.commit()

        print(f"Imported {len(rooms)} rooms successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")

    finally:
        db.close()