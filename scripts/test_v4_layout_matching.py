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
    (
        "Duplex Junior Suite",
        "Loft Junior Suite",
        False,
    ),
    (
        "Duplex Junior Suite",
        "Split Level Junior Suite",
        False,
    ),
    (
        "Duplex Junior Suite",
        "Deluxe Duplex Junior Suite",
        True,
    ),
    (
        "Duplex Junior Suite",
        "Junior Suite",
        True,
    ),
]


for name_a, name_b, expected in test_pairs:
    room_a = prepare_room(name_a)
    room_b = prepare_room(name_b)

    result = is_match_v4(room_a, room_b)

    print(f"\n{name_a}  VS  {name_b}")
    print("Layout A:", room_a["features"]["layout"])
    print("Layout B:", room_b["features"]["layout"])
    print("Result  :", result)
    print("Expected:", expected)
    print("Status  :", "PASS" if result == expected else "FAIL")