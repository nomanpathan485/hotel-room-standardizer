import json

import pandas as pd


ERROR_FILE = "data/model_errors.csv"
OUTPUT_FILE = "data/classified_errors.csv"


def classify_error(row):
    if row["label"] == 0 and row["predicted"] == 1:
        return "wrong_merge"

    if row["label"] == 1 and row["predicted"] == 0:
        return "wrong_split"

    return "not_an_error"


def find_conflicts(row):
    conflicts = []

    features_a = json.loads(row["room_a_features"])
    features_b = json.loads(row["room_b_features"])

    bedroom_count_a = features_a.get("bedroom_count")
    bedroom_count_b = features_b.get("bedroom_count")

    if row["same_category"] == 0:
        conflicts.append("category_conflict")

    if (
        row["room_class_both_known"] == 1
        and row["same_room_class"] == 0
    ):
        conflicts.append("room_class_conflict")

    if (
        row["view_both_known"] == 1
        and row["same_view"] == 0
    ):
        conflicts.append("view_conflict")

    if (
        row["bed_type_both_known"] == 1
        and row["same_bed_type"] == 0
    ):
        conflicts.append("bed_type_conflict")

    if (
        row["bed_config_both_present"] == 1
        and row["same_bed_configuration"] == 0
    ):
        conflicts.append("bed_configuration_conflict")

    if (
        row["occupancy_both_known"] == 1
        and row["same_occupancy"] == 0
    ):
        conflicts.append("occupancy_conflict")

    if row["single_use_mismatch"] == 1:
        conflicts.append("single_use_mismatch")

    if row["balcony_mismatch"] == 1:
        conflicts.append("balcony_mismatch")

    if (
        bedroom_count_a is not None
        and bedroom_count_b is not None
        and bedroom_count_a != bedroom_count_b
    ):
        conflicts.append("bedroom_count_conflict")

    if not conflicts:
        conflicts.append("no_detected_conflict")

    return "|".join(conflicts)


df = pd.read_csv(ERROR_FILE)

df["error_type"] = df.apply(
    classify_error,
    axis=1,
)

df["detected_conflicts"] = df.apply(
    find_conflicts,
    axis=1,
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\nError type counts:")
print(df["error_type"].value_counts())

print("\nDetected conflict counts:")
print(
    df["detected_conflicts"]
    .str.split("|")
    .explode()
    .value_counts()
)

print(f"\nSaved to {OUTPUT_FILE}")

exploded = df.assign(
    detected_conflicts=df["detected_conflicts"].str.split("|")
).explode(
    "detected_conflicts",
    ignore_index=True,
)

print("\nConflicts by error type:")
print(
    pd.crosstab(
        exploded["detected_conflicts"],
        exploded["error_type"],
    ).to_string()
)

unexplained_wrong_merges = df[
    (df["error_type"] == "wrong_merge")
    & (df["detected_conflicts"] == "no_detected_conflict")
]

sample = unexplained_wrong_merges.sample(
    n=min(20, len(unexplained_wrong_merges)),
    random_state=42,
)

print("\nSample unexplained wrong merges:")
print(
    sample[
        [
            "hotel_id",
            "room_a_name",
            "room_b_name",
            "fuzzy_score",
        ]
    ].to_string(index=False)
)