from app.services.model_loader import load_room_matcher_model
from app.services.pair_feature_extractor import extract_pair_features
from app.services.ml_feature_schema import FEATURE_COLUMNS

_model = load_room_matcher_model()


def predict_room_match(
    room_a_name: str,
    room_b_name: str,
) -> dict:
    pair_features = extract_pair_features(
        room_a_name=room_a_name,
        room_b_name=room_b_name,
    )

    model_input = [
        [pair_features[column] for column in FEATURE_COLUMNS]
    ]

    prediction = int(_model.predict(model_input)[0])
    match_probability = float(
        _model.predict_proba(model_input)[0][1]
    )

    return {
        "is_match": bool(prediction),
        "match_probability": round(match_probability, 4),
        "features": pair_features,
    }