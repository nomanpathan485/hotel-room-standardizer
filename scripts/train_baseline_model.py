import pandas as pd
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
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
MODEL_PATH = "models/room_matcher_pipeline.joblib"

joblib.dump(model, MODEL_PATH)

print(f"\nSaved trained model to {MODEL_PATH}")

validation_predictions = model.predict(X_validation)


validation_results = validation_df.copy()

validation_results["actual"] = y_validation
validation_results["predicted"] = validation_predictions
validation_results.to_csv(
    "data/all_validation_predictions.csv",
    index=False,
)

errors = validation_results[
    validation_results["actual"] != validation_results["predicted"]
]

errors.to_csv(
    "data/model_errors.csv",
    index=False,
)

print(f"\nSaved {len(errors)} errors to data/model_errors.csv")


print("Validation accuracy:")
print(accuracy_score(y_validation, validation_predictions))

print("\nConfusion matrix:")
print(confusion_matrix(y_validation, validation_predictions))

print("\nClassification report:")
print(
    classification_report(
        y_validation,
        validation_predictions,
        digits=4,
    )
)
classifier = model.named_steps["classifier"]

feature_weights = pd.DataFrame(
    {
        "feature": FEATURE_COLUMNS,
        "weight": classifier.coef_[0],
    }
)

feature_weights["absolute_weight"] = feature_weights["weight"].abs()

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