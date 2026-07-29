from app.services.feature_extractor import extract_features
from app.services.matcher import is_match_v4
from app.services.normalizer import normalize_room_name


def prepare_room(room_name: str) -> dict:
    return {
        "room_name": room_name,
        "normalized_name": normalize_room_name(room_name),
        "features": extract_features(room_name),
    }


test_pairs = [
    ("Deluxe Sea View", "Deluxe Room Sea View", True),
    ("Junior Sea View", "Junior Suite Sea View", True),
    ("Deluxe Room Sea View", "Deluxe Suite Sea View", False),
    ("Deluxe Villa Sea View", "Deluxe Apartment Sea View", False),
]


for name_a, name_b, expected in test_pairs:
    room_a = prepare_room(name_a)
    room_b = prepare_room(name_b)

    result = is_match_v4(room_a, room_b)

    print(f"\n{name_a}  VS  {name_b}")
    print("Category A:", room_a["features"]["category"])
    print("Category B:", room_b["features"]["category"])
    print("Result    :", result)
    print("Expected  :", expected)
    print("Status    :", "PASS" if result == expected else "FAIL")