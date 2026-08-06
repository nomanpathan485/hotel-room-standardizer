import pandas as pd

from app.services.ml_feature_schema import FEATURE_COLUMNS


train_df = pd.read_csv("data/train_features.csv")

negative_pairs = train_df[train_df["label"] == 0]
positive_pairs = train_df[train_df["label"] == 1]

coverage = pd.DataFrame({
    "negative_mean": negative_pairs[FEATURE_COLUMNS].mean(),
    "positive_mean": positive_pairs[FEATURE_COLUMNS].mean(),
})

coverage["difference"] = (
    coverage["positive_mean"]
    - coverage["negative_mean"]
)

coverage = coverage.sort_values(
    by="difference",
    ascending=False,
)

print(coverage.to_string())