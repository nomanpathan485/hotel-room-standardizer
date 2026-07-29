import pandas as pd


ERROR_FILE = "data/error_analysis.csv"


OCCUPANCY_TERMS = [
    "single",
    "double",
    "triple",
    "quad",
    "quadruple",
    "5 person",
    "4 person",
    "3 person",
    "2 person",
    "2+1",
    "2+2",
]

SINGLE_USE_TERMS = [
    "single use",
    "single occupancy",
    "for 1 person",
    "1 person",
]

BED_TERMS = [
    "twin bed",
    "twin beds",
    "double bed",
    "king bed",
    "queen bed",
    "bunk bed",
    "sofa bed",
]

VIEW_TERMS = [
    "sea view",
    "side sea",
    "garden view",
    "land view",
    "pool view",
    "city view",
    "ocean view",
]


def contains_any(text, terms):
    text = str(text).lower()
    return any(term in text for term in terms)


def classify_error(row):
    combined_text = (
        f"{row['room_a_name']} "
        f"{row['room_b_name']}"
    )

    causes = []

    if contains_any(combined_text, SINGLE_USE_TERMS):
        causes.append("single_use")

    if contains_any(combined_text, OCCUPANCY_TERMS):
        causes.append("occupancy")

    if contains_any(combined_text, BED_TERMS):
        causes.append("bed")

    if contains_any(combined_text, VIEW_TERMS):
        causes.append("view")

    if row["label"] == 0 and row["predicted_label"] == 1:
        error_type = "wrong_merge"
    else:
        error_type = "wrong_split"

    if not causes:
        causes.append("unknown")

    return error_type, "|".join(causes)


df = pd.read_csv(ERROR_FILE)

classified = df.apply(
    classify_error,
    axis=1,
    result_type="expand",
)

df["error_type"] = classified[0]
df["possible_causes"] = classified[1]

df.to_csv(
    "data/classified_errors.csv",
    index=False,
)

print("\nError type counts:")
print(df["error_type"].value_counts())

print("\nPossible cause counts:")
print(
    df["possible_causes"]
    .str.split("|")
    .explode()
    .value_counts()
)

print("\nSaved to data/classified_errors.csv")