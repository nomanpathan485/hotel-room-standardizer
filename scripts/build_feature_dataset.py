import csv
import json

from app.services.feature_extractor import extract_features
from app.services.pair_feature_extractor import extract_pair_features


INPUT_FILE = "data/training_pairs.csv"
OUTPUT_FILE = "data/training_features.csv"


def build_feature_dataset():
    feature_rows = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            room_a_features = extract_features(row["room_a_name"])
            room_b_features = extract_features(row["room_b_name"])
            pair_features = extract_pair_features(
                room_a_name=row["room_a_name"],
                room_b_name=row["room_b_name"],
            )

            feature_rows.append(
                {
                    "case_id": row["case_id"],
                    "hotel_id": row["hotel_id"],
                    "room_a_index": row["room_a_index"],
                    "room_b_index": row["room_b_index"],
                    "room_a_name": row["room_a_name"],
                    "room_b_name": row["room_b_name"],
                    "room_a_features": json.dumps(
                        room_a_features,
                        ensure_ascii=False,
                    ),
                    "room_b_features": json.dumps(
                        room_b_features,
                        ensure_ascii=False,
                    ),
                    **pair_features,
                    "label": int(row["label"]),
                }
            )

    if not feature_rows:
        print("No training pairs found.")
        return

    fieldnames = list(feature_rows[0].keys())

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(feature_rows)

    print("#" * 70)
    print("FEATURE DATASET CREATED")
    print("#" * 70)

    print(f"Total rows: {len(feature_rows)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nFirst 5 feature rows:\n")

    for row in feature_rows[:5]:
        print(row)


if __name__ == "__main__":
    build_feature_dataset()