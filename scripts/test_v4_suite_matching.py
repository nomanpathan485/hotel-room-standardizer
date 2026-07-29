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
    ("Junior Suite", "Royal Suite", False),
    ("Family Suite", "Junior Suite", False),
    ("Junior Suite", "Deluxe Junior Suite", True),
    ("Junior Suite", "Suite", True),
]


for name_a, name_b, expected in test_pairs:
    result = is_match_v4(
        prepare_room(name_a),
        prepare_room(name_b),
    )

    print(f"\n{name_a}  VS  {name_b}")
    print("Result  :", result)
    print("Expected:", expected)
    print("Status  :", "PASS" if result == expected else "FAIL")