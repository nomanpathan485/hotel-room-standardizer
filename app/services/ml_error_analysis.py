from app.services.ml_matcher import predict_room_match
from app.services.feature_extractor import extract_features


def analyze_room_pair(room_a: str, room_b: str):
    features_a = extract_features(room_a)
    features_b = extract_features(room_b)

    prediction = predict_room_match(room_a, room_b)

    print("=" * 80)
    print("ROOM A")
    print(room_a)
    print(features_a)

    print()

    print("ROOM B")
    print(room_b)
    print(features_b)

    print()

    print("Prediction")
    print(prediction)

    print("=" * 80)