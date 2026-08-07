from app.services.feature_extractor import extract_features
from app.services.matcher import decide_room_match_ml


name_a = "1 KING CLASSIC"
name_b = "Classic King Room"

print("FEATURES A:")
print(extract_features(name_a))

print("\nFEATURES B:")
print(extract_features(name_b))

print("\nDECISION:")
print(
    decide_room_match_ml(
        {"room_name": name_a},
        {"room_name": name_b},
    )
)