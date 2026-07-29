import json
import pandas as pd

# Load the feature dataset
df = pd.read_csv("data/training_features.csv")

# Load the frozen hotel split
with open("data/dataset_split.json", "r") as f:
    split = json.load(f)

# Create train, validation and test datasets
train_df = df[df["hotel_id"].astype(str).isin(split["train"])]
validation_df = df[df["hotel_id"].astype(str).isin(split["validation"])]
test_df = df[df["hotel_id"].astype(str).isin(split["test"])]

# Save them
train_df.to_csv("data/train_features.csv", index=False)
validation_df.to_csv("data/validation_features.csv", index=False)
test_df.to_csv("data/test_features.csv", index=False)

print(f"Train pairs: {len(train_df)}")
print(f"Validation pairs: {len(validation_df)}")
print(f"Test pairs: {len(test_df)}")