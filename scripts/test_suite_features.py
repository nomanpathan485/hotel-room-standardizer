from app.services.feature_extractor import extract_features


test_names = [
    "Deluxe Family Suite",
    "Deluxe Family Duplex Room",
    "Deluxe Suite",
    "Junior Suite",
    "Royal Suite",
    "Junior Suite Deluxe 2 Rooms with Balcony",
    "DELUXE SEA VIEW",
]

for name in test_names:
    features = extract_features(name)

    print(f"\n{name}")
    print("category   :", features["category"])
    print("suite_type :", features["suite_type"])