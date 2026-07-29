from app.services.feature_extractor import extract_features


test_cases = [
    ("Deluxe Family Duplex Suite", "suite", "duplex"),
    ("Deluxe Family Dublex Room", "room", "duplex"),
    ("Split-Level Junior Suite", "suite", "split_level"),
    ("Bi Level Apartment", "apartment", "split_level"),
    ("Maisonette", "unknown", "maisonette"),
    ("Loft Apartment", "apartment", "loft"),
    ("Mezzanine Villa", "villa", "mezzanine"),
    ("Deluxe Suite", "suite", "unknown"),
]


for room_name, expected_category, expected_layout in test_cases:
    features = extract_features(room_name)

    actual_category = features["category"]
    actual_layout = features["layout"]

    passed = (
        actual_category == expected_category
        and actual_layout == expected_layout
    )

    print(f"\nRoom name         : {room_name}")
    print("Category          :", actual_category)
    print("Expected category :", expected_category)
    print("Layout            :", actual_layout)
    print("Expected layout   :", expected_layout)
    print("Status            :", "PASS" if passed else "FAIL")