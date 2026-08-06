import pandas as pd
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    fbeta_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from app.services.ml_feature_schema import FEATURE_COLUMNS




train_df = pd.read_csv("data/train_features.csv")
validation_df = pd.read_csv("data/validation_features.csv")


X_train = train_df[FEATURE_COLUMNS].to_numpy()
y_train = train_df["label"].to_numpy()

X_validation = validation_df[FEATURE_COLUMNS].to_numpy()
y_validation = validation_df["label"].to_numpy()


model = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        (
            "classifier",
            LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
            ),
        ),
    ]
)


model.fit(X_train, y_train)

validation_probabilities = model.predict_proba(
    X_validation
)[:, 1]

candidate_thresholds = [
    0.50,
    0.60,
    0.70,
    0.80,
    0.85,
    0.90,
]

threshold_results = []

print("\nThreshold comparison:")

for threshold in candidate_thresholds:
    predictions = (
        validation_probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_validation,
        predictions,
        labels=[0, 1],
    ).ravel()

    f05_score = fbeta_score(
        y_validation,
        predictions,
        beta=0.5,
        zero_division=0,
    )

    threshold_results.append(
        {
            "threshold": threshold,
            "f0.5": f05_score,
            "false_merges": fp,
            "false_splits": fn,
        }
    )

    print(
        f"Threshold={threshold:.2f} | "
        f"False merges={fp} | "
        f"False splits={fn} | "
        f"True matches={tp} | "
        f"F0.5={f05_score:.4f}"
    )

best_result = max(
    threshold_results,
    key=lambda result: (
        result["f0.5"],
        -result["false_merges"],
        result["threshold"],
    ),
)

selected_threshold = best_result["threshold"]

validation_predictions = (
    validation_probabilities >= selected_threshold
).astype(int)

print(
    f"\nSelected threshold: "
    f"{selected_threshold:.2f}"
)

MODEL_PATH = "models/room_matcher_pipeline.joblib"

model_artifact = {
    "model": model,
    "feature_columns": list(FEATURE_COLUMNS),
    "threshold": selected_threshold,
}

joblib.dump(model_artifact, MODEL_PATH)

print(f"Saved trained model to {MODEL_PATH}")

validation_results = validation_df.copy()
validation_results["actual"] = y_validation
validation_results["probability"] = validation_probabilities
validation_results["predicted"] = validation_predictions

validation_results.to_csv(
    "data/all_validation_predictions.csv",
    index=False,
)

errors = validation_results[
    validation_results["actual"]
    != validation_results["predicted"]
]

errors.to_csv(
    "data/model_errors.csv",
    index=False,
)

print(
    f"\nSaved {len(errors)} errors "
    "to data/model_errors.csv"
)

print("\nValidation accuracy:")
print(
    accuracy_score(
        y_validation,
        validation_predictions,
    )
)

print("\nConfusion matrix:")
print(
    confusion_matrix(
        y_validation,
        validation_predictions,
        labels=[0, 1],
    )
)

print("\nClassification report:")
print(
    classification_report(
        y_validation,
        validation_predictions,
        digits=4,
        zero_division=0,
    )
)
classifier = model.named_steps["classifier"]

feature_weights = pd.DataFrame(
    {
        "feature": FEATURE_COLUMNS,
        "weight": classifier.coef_[0],
    }
)

feature_weights["absolute_weight"] = (
    feature_weights["weight"].abs()
)

feature_weights = feature_weights.sort_values(
    by="absolute_weight",
    ascending=False,
)

print("\nFeature weights:")
print(
    feature_weights[
        ["feature", "weight"]
    ].to_string(index=False)
)