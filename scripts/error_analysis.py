import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "fuzzy_score",
    "same_category",
    "room_class_both_known",
    "same_room_class",
    "view_both_known",
    "same_view",
    "bed_type_both_known",
    "same_bed_type",
    "bed_config_both_present",
    "same_bed_configuration",
    "same_balcony",
]


train_df = pd.read_csv("data/train_features.csv")
validation_df = pd.read_csv("data/validation_features.csv")


X_train = train_df[FEATURE_COLUMNS]
y_train = train_df["label"]

X_validation = validation_df[FEATURE_COLUMNS]
y_validation = validation_df["label"]


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

validation_df["predicted_label"] = model.predict(X_validation)

validation_df["probability"] = model.predict_proba(X_validation)[:, 1]

errors = validation_df[
    validation_df["label"] != validation_df["predicted_label"]
]

errors = errors.sort_values(
    by="probability",
    ascending=False,
)

errors.to_csv(
    "data/error_analysis.csv",
    index=False,
)

print(f"Total errors: {len(errors)}")
print("Saved to data/error_analysis.csv")