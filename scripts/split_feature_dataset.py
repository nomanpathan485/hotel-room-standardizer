import json

import pandas as pd


INPUT_PATH = "data/training_features_clean.csv"

TRAIN_OUTPUT_PATH = "data/train_features_clean.csv"
VALIDATION_OUTPUT_PATH = "data/validation_features_clean.csv"
TEST_OUTPUT_PATH = "data/test_features_clean.csv"

SPLIT_PATH = "data/dataset_split.json"


# Load the cleaned feature dataset
df = pd.read_csv(INPUT_PATH)

# Load the frozen hotel-level split
with open(SPLIT_PATH, "r", encoding="utf-8") as file:
    split = json.load(file)


# Convert all hotel IDs to strings for consistent comparison
hotel_ids = df["hotel_id"].astype(str)

train_hotel_ids = set(map(str, split["train"]))
validation_hotel_ids = set(map(str, split["validation"]))
test_hotel_ids = set(map(str, split["test"]))


# Create train, validation, and test datasets
train_df = df[
    hotel_ids.isin(train_hotel_ids)
].copy()

validation_df = df[
    hotel_ids.isin(validation_hotel_ids)
].copy()

test_df = df[
    hotel_ids.isin(test_hotel_ids)
].copy()


# Save the cleaned splits
train_df.to_csv(
    TRAIN_OUTPUT_PATH,
    index=False,
)

validation_df.to_csv(
    VALIDATION_OUTPUT_PATH,
    index=False,
)

test_df.to_csv(
    TEST_OUTPUT_PATH,
    index=False,
)


# Display split sizes
print(f"Total clean pairs: {len(df)}")
print(f"Train pairs: {len(train_df)}")
print(f"Validation pairs: {len(validation_df)}")
print(f"Test pairs: {len(test_df)}")


# Verify that no hotel appears in multiple splits
actual_train_hotels = set(
    train_df["hotel_id"].astype(str)
)

actual_validation_hotels = set(
    validation_df["hotel_id"].astype(str)
)

actual_test_hotels = set(
    test_df["hotel_id"].astype(str)
)

assert actual_train_hotels.isdisjoint(
    actual_validation_hotels
)

assert actual_train_hotels.isdisjoint(
    actual_test_hotels
)

assert actual_validation_hotels.isdisjoint(
    actual_test_hotels
)


# Verify that every clean row was assigned to a split
split_row_count = (
    len(train_df)
    + len(validation_df)
    + len(test_df)
)

assert split_row_count == len(df), (
    f"Rows were lost during splitting: "
    f"input={len(df)}, output={split_row_count}"
)


# Verify that all 33 model features exist
required_columns = {
    "fuzzy_score",
    "ordinary_ratio",
    "token_sort_ratio",
    "token_count_ratio",
    "character_length_ratio",
    "same_category",
    "identity_tokens_both_present",
    "shared_identity_token",
    "identity_token_overlap_ratio",
    "identity_token_mismatch",
    "room_class_both_known",
    "same_room_class",
    "view_both_known",
    "same_view",
    "bed_type_both_known",
    "same_bed_type",
    "bed_type_compatible",
    "bed_config_both_present",
    "same_bed_configuration",
    "bedroom_count_both_known",
    "same_bedroom_count",
    "occupancy_both_known",
    "same_occupancy",
    "both_single_use",
    "single_use_mismatch",
    "both_balcony",
    "balcony_mismatch",
    "both_pool_access",
    "pool_access_mismatch",
    "both_swim_up",
    "swim_up_mismatch",
    "luxury_variant_mismatch",
    "overwater_mismatch",
}

for split_name, split_df in {
    "train": train_df,
    "validation": validation_df,
    "test": test_df,
}.items():
    missing_columns = required_columns - set(split_df.columns)

    assert not missing_columns, (
        f"{split_name} split is missing columns: "
        f"{sorted(missing_columns)}"
    )


print("PASS: No hotel leakage")
print("PASS: No rows lost")
print("PASS: All 33 ML features exist in every split")

print(f"Saved: {TRAIN_OUTPUT_PATH}")
print(f"Saved: {VALIDATION_OUTPUT_PATH}")
print(f"Saved: {TEST_OUTPUT_PATH}")