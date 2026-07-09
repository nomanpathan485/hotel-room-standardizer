from app.services.grouping_engine import group_rooms

rooms = [
    {
        "id": 1,
        "supplier": "Supplier A",
        "room_name": "Deluxe King Room"
    },
    {
        "id": 2,
        "supplier": "Supplier B",
        "room_name": "King Deluxe Room"
    },
    {
        "id": 3,
        "supplier": "Supplier C",
        "room_name": "Twin Room"
    },
    {
        "id": 4,
        "supplier": "Supplier D",
        "room_name": "Twin Room Single Use"
    }
]

groups = group_rooms(rooms)

for group in groups:
    print(f"\nGroup ID: {group['group_id']}")

    for room in group["rooms"]:
        print(f"  - {room['room_name']} ({room['supplier']})")