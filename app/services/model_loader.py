from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "room_matcher_hgb.joblib"
)


def load_room_matcher_model() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained HGB model not found at: {MODEL_PATH}. "
            "Run python -m scripts.train_hist_gradient_boosting first."
        )

    model_bundle = joblib.load(MODEL_PATH)

    required_keys = {
        "model",
        "feature_columns",
        "threshold",
        "model_type",
    }

    missing_keys = required_keys - set(model_bundle)

    if missing_keys:
        raise ValueError(
            "Invalid model bundle. Missing keys: "
            f"{sorted(missing_keys)}"
        )

    return model_bundle