from pathlib import Path

import joblib


MODEL_PATH = Path("models/room_matcher_pipeline.joblib")


def load_room_matcher_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at: {MODEL_PATH}. "
            "Run the training script first."
        )

    return joblib.load(MODEL_PATH)