from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    confusion_matrix,
    fbeta_score,
    precision_score,
    recall_score,
)

from app.services.ml_feature_schema import FEATURE_COLUMNS


TRAIN_PATH = "data/train_features_clean.csv"
VALIDATION_PATH = "data/validation_features_clean.csv"
MODEL_PATH = "models/room_matcher_hgb.joblib"

TARGET_PRECISION = 0.85


# Load only training and validation data.
# The test dataset must remain untouched.
train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)


X_train = train_df[FEATURE_COLUMNS]
y_train = train_df["label"]

X_validation = validation_df[FEATURE_COLUMNS]
y_validation = validation_df["label"]


print(f"Training pairs: {len(train_df)}")
print(f"Validation pairs: {len(validation_df)}")

print("\nTraining labels:")
print(y_train.value_counts().sort_index())

print("\nValidation labels:")
print(y_validation.value_counts().sort_index())


model = HistGradientBoostingClassifier(
    learning_rate=0.05,
    max_iter=300,
    max_leaf_nodes=15,
    min_samples_leaf=20,
    l2_regularization=1.0,
    early_stopping=True,
    validation_fraction=0.15,
    random_state=42,
)


print("\nTraining HistGradientBoostingClassifier...")

model.fit(
    X_train,
    y_train,
)

print("Training completed.")


validation_probabilities = model.predict_proba(
    X_validation
)[:, 1]


def calculate_metrics(threshold):
    predictions = (
        validation_probabilities >= threshold
    ).astype(int)

    true_negative, false_positive, false_negative, true_positive = (
        confusion_matrix(
            y_validation,
            predictions,
            labels=[0, 1],
        ).ravel()
    )

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    f_beta = fbeta_score(
        y_validation,
        predictions,
        beta=0.5,
        zero_division=0,
    )

    return {
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f0.5": f_beta,
        "false_merges": false_positive,
        "false_splits": false_negative,
        "true_matches": true_positive,
        "true_negatives": true_negative,
        "predicted_matches": int(predictions.sum()),
    }


threshold_results = []

for threshold_number in range(50, 100):
    threshold = threshold_number / 100

    threshold_results.append(
        calculate_metrics(threshold)
    )


results_df = pd.DataFrame(threshold_results)

qualified_results = results_df[
    results_df["precision"] >= TARGET_PRECISION
]


if not qualified_results.empty:
    selected_result = qualified_results.sort_values(
        by=["recall", "f0.5"],
        ascending=False,
    ).iloc[0]

    selection_reason = (
        f"highest recall with precision >= "
        f"{TARGET_PRECISION:.0%}"
    )
else:
    selected_result = results_df.sort_values(
        by="f0.5",
        ascending=False,
    ).iloc[0]

    selection_reason = (
        "target precision was not reached; "
        "selected highest F0.5"
    )


selected_threshold = float(
    selected_result["threshold"]
)


print("\nThreshold comparison:")
print(
    results_df[
        [
            "threshold",
            "precision",
            "recall",
            "f0.5",
            "false_merges",
            "false_splits",
            "predicted_matches",
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 70)
print("SELECTED VALIDATION RESULT")
print(f"Reason: {selection_reason}")
print(f"Threshold: {selected_threshold:.2f}")
print(f"Precision: {selected_result['precision']:.4f}")
print(f"Recall: {selected_result['recall']:.4f}")
print(f"F0.5: {selected_result['f0.5']:.4f}")
print(f"False merges: {int(selected_result['false_merges'])}")
print(f"False splits: {int(selected_result['false_splits'])}")
print(f"True matches: {int(selected_result['true_matches'])}")


Path("models").mkdir(
    parents=True,
    exist_ok=True,
)

model_bundle = {
    "model": model,
    "feature_columns": FEATURE_COLUMNS,
    "threshold": selected_threshold,
    "model_type": "HistGradientBoostingClassifier",
}

joblib.dump(
    model_bundle,
    MODEL_PATH,
)

print(f"\nSaved model: {MODEL_PATH}")
print("PASS: Test dataset was not used")