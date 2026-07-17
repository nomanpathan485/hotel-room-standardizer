from app.services.feature_extractor import extract_features

tests = [
    "Duplex Suite",
    "Duplex Suite 2 Sofa Beds",
]

for room_name in tests:
    features = extract_features(room_name)

    print("\nROOM:", room_name)
    print("BED TYPE:", features.get("bed_type"))
    print("BED CONFIG:", features.get("bed_configuration"))