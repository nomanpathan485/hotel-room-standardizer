from app.services.feature_extractor import extract_features
tests = [
    "standard double or twin room land view 1 double bed and 2 single sofa beds",
    "standard double or twin room land view 1 double bed and 2 twin sofa beds",
]
for room_name in tests:
    features = extract_features(room_name)

    print("\n" + "=" * 60)
    print("ROOM:", room_name)
    print("BED CONFIG:", features.get("bed_configuration"))