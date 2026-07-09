import json

from app.database import SessionLocal
from app.models import Room
from app.services.matcher import find_best_match

# Connect to the database
db = SessionLocal()

# Load all room names
rooms = db.query(Room).all()
room_names = [room.supplier_room_name for room in rooms]

# Load test cases
with open("evaluation_dataset.json", "r") as file:
    test_cases = json.load(file)

correct = 0

for test in test_cases:
    query = test["query"]
    expected = test["expected"]

    # Find the best match
    prediction, score = find_best_match(query, room_names)

    print("Score :", round(score, 2))

    print("\n----------------------------")
    print("Query      :", query)
    print("Expected   :", expected)
    print("Prediction :", prediction)
    print("Score :", round(score, 2))
    

    if prediction == expected:
        correct += 1

print("\n============================")
print(f"Accuracy: {correct}/{len(test_cases)}")

db.close()