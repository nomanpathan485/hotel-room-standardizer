from app.services.feature_extractor import extract_features
from app.services.response_formatter import format_category


test_cases = [
    ("Duplex Junior Suite", "Duplex Junior Suite"),
    ("Loft Apartment", "Loft Apartment"),
    ("Mezzanine Villa", "Mezzanine Villa"),
]


for room_name, expected in test_cases:
    features = extract_features(room_name)
    result = format_category(features, room_name)

    print(f"\nRoom name : {room_name}")
    print("Layout    :", features["layout"])
    print("Result    :", result)
    print("Expected  :", expected)
    print("Status    :", "PASS" if result == expected else "FAIL")