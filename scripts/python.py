from pprint import pprint

from app.services.feature_extractor import extract_features
from app.services.matcher import (
    decide_room_match_ml,
    is_class_only_equivalent,
)


test_pairs = [
    # These must match.
    ("DELUXE", "Deluxe Room", True),
    ("Room Deluxe", "Deluxe Guest Room", True),
    ("PREMIUM", "Premium Room", True),
    ("SUPERIOR", "Superior Guestroom", True),

    # These must not match.
    ("Deluxe", "Deluxe Suite", False),
    ("Deluxe", "Deluxe Sea View Room", False),
    ("Premium", "Premium Family Room", False),
    ("Deluxe", "Executive Room", False),
]


for room_a_name, room_b_name, expected_match in test_pairs:
    room_a = {
        "supplier_room_name": room_a_name,
        "normalized_name": room_a_name.lower(),
        "features": extract_features(room_a_name),
    }

    room_b = {
        "supplier_room_name": room_b_name,
        "normalized_name": room_b_name.lower(),
        "features": extract_features(room_b_name),
    }

    rule_result = is_class_only_equivalent(
        room_a["normalized_name"],
        room_b["normalized_name"],
    )

    decision = decide_room_match_ml(room_a, room_b)
    actual_match = decision.value.lower() == "match"

    print("\n" + "=" * 70)
    print(f"ROOM A: {room_a_name}")
    print(f"ROOM B: {room_b_name}")
    print(f"EXPECTED MATCH: {expected_match}")
    print(f"CLASS-ONLY RULE: {rule_result}")
    print(f"FINAL DECISION: {decision.value}")
    print(f"TEST PASSED: {actual_match == expected_match}")

    if actual_match != expected_match:
        print("\nROOM A FEATURES")
        pprint(room_a["features"])

        print("\nROOM B FEATURES")
        pprint(room_b["features"])