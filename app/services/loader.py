import json

from app.database import SessionLocal
from app.models import Room


def import_rooms():
    db = SessionLocal()
    db.query(Room).delete()
    db.commit()
    print("Old rooms removed.")

    try:
        # Open the JSON file
        with open("data/hotel_dataset_8.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        rooms = data["roomRates"]

        print(type(rooms))
        print(len(rooms))

        # Insert each room into the database
        for room in rooms:
            new_room = Room(
                supplier_code=room["index"],
                supplier_name=room["provider"],
                supplier_room_name=room["roomName"],
                standard_room_name=None,

                code=room.get("code"),
                provider_hotel_id=room.get("providerHotelId"),
                board_basis=room.get("boardBasis"),
                beds=str(room.get("beds")) if room.get("beds") is not None else None,
                room_description=room.get("roomDescription"),
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

if __name__ == "__main__":
    import_rooms()