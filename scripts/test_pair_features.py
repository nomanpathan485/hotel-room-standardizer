from app.services.pair_feature_extractor import (
    extract_pair_features,
)


room_a = "Premium Double Room"
room_b = "PREMIUM DOUBLE ROOM (FULL DOUBLE BED)"


features = extract_pair_features(
    room_a,
    room_b,
)


print("Room A:", room_a)
print("Room B:", room_b)

print("\nPair features:")

for feature_name, value in features.items():
    print(f"{feature_name}: {value}")