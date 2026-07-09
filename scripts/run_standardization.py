from app.database import SessionLocal
from app.models import Room
from app.services.llm import generate_canonical_name

# Create a database session
db = SessionLocal()

# Load all rooms
rooms = db.query(Room).all()

print(f"Loaded {len(rooms)} rooms\n")

for room in rooms:
    # Skip rooms that are already standardized
    if room.standard_room_name:
        continue

    print(f"Processing: {room.supplier_room_name}")

    # Generate the canonical room name using the LLM
    canonical_name = generate_canonical_name(room.supplier_room_name)

    print(f"Canonical : {canonical_name}\n")

    # Save the result
    room.standard_room_name = canonical_name

# Save all changes to the database
db.commit()

db.close()

print("✅ Standardization completed.")