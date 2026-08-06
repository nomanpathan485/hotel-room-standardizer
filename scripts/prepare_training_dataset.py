import pandas as pd

from app.services.normalizer import normalize_room_name


INPUT_PATH = "data/training_features.csv"
OUTPUT_PATH = "data/training_features_clean.csv"
CONFLICTS_PATH = "data/conflicting_pair_labels.csv"


df = pd.read_csv(INPUT_PATH)

print(f"Original rows: {len(df)}")


def build_pair_key(row):
    normalized_names = sorted(
        [
            normalize_room_name(str(row["room_a_name"])),
            normalize_room_name(str(row["room_b_name"])),
        ]
    )

    return (
        f"{str(row['hotel_id'])}"
        f"|||{normalized_names[0]}"
        f"|||{normalized_names[1]}"
    )


df["pair_key"] = df.apply(build_pair_key, axis=1)

label_counts = (
    df.groupby("pair_key")["label"]
    .nunique()
)

conflicting_keys = set(
    label_counts[label_counts > 1].index
)

conflicting_rows = df[
    df["pair_key"].isin(conflicting_keys)
].copy()

conflicting_rows.to_csv(
    CONFLICTS_PATH,
    index=False,
)

clean_df = df[
    ~df["pair_key"].isin(conflicting_keys)
].copy()

clean_df = clean_df.drop_duplicates(
    subset=["pair_key"],
    keep="first",
)

clean_df = clean_df.drop(columns=["pair_key"])

clean_df.to_csv(
    OUTPUT_PATH,
    index=False,
)

removed_duplicates = (
    len(df)
    - len(conflicting_rows)
    - len(clean_df)
)

print(f"Conflicting pair keys: {len(conflicting_keys)}")
print(f"Rows belonging to conflicts: {len(conflicting_rows)}")
print(f"Duplicate rows removed: {removed_duplicates}")
print(f"Clean rows saved: {len(clean_df)}")
print(f"Clean dataset: {OUTPUT_PATH}")
print(f"Conflict report: {CONFLICTS_PATH}")

assert clean_df["label"].isin([0, 1]).all()
assert clean_df.isna().sum().sum() == 0

print("PASS: Labels are valid")
print("PASS: Clean dataset contains no missing values")