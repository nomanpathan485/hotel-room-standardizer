import pandas as pd

from app.services.ml_feature_schema import FEATURE_COLUMNS
from app.services.model_loader import load_room_matcher_model
from app.services.pair_feature_extractor import extract_pair_features


AMBIGUOUS_THRESHOLD = 0.79
AUTO_MATCH_THRESHOLD = 0.89


_model_bundle = load_room_matcher_model()

_model = _model_bundle["model"]
_model_feature_columns = _model_bundle["feature_columns"]
_model_type = _model_bundle["model_type"]


if list(_model_feature_columns) != list(FEATURE_COLUMNS):
    raise ValueError(
        "The application feature schema does not match "
        "the trained model feature schema."
    )


def predict_room_match(
    room_a_name: str,
    room_b_name: str,
) -> dict:
    pair_features = extract_pair_features(
        room_a_name=room_a_name,
        room_b_name=room_b_name,
    )

    model_input = pd.DataFrame(
        [
            {
                column: pair_features[column]
                for column in _model_feature_columns
            }
        ],
        columns=_model_feature_columns,
    )

    match_probability = float(
        _model.predict_proba(model_input)[0][1]
    )

    if match_probability >= AUTO_MATCH_THRESHOLD:
        decision = "match"
    elif match_probability >= AMBIGUOUS_THRESHOLD:
        decision = "ambiguous"
    else:
        decision = "no_match"

    return {
        "is_match": decision == "match",
        "decision": decision,
        "match_probability": round(
            match_probability,
            4,
        ),
        "model_type": _model_type,
        "features": pair_features,
    }