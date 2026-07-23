import csv
from collections import defaultdict


TRAINING_FILE = "data/training_pairs.csv"


def normalize_pair(room_a: str, room_b: str) -> tuple[str, str]:
    room_a = room_a.strip().lower()
    room_b = room_b.strip().lower()

    return tuple(sorted([room_a, room_b]))


def check_training_dataset():
    pair_labels = defaultdict(set)
    pair_counts = defaultdict(int)

    with open(
        TRAINING_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            name_pair = normalize_pair(
                row["room_a_name"],
                row["room_b_name"],
            )
            pair_key = (
                row["hotel_id"],
                *name_pair,
            )

            label = int(row["label"])

            pair_labels[pair_key].add(label)
            pair_counts[(pair_key, label)] += 1

    conflicts = []
    duplicate_positive = 0
    duplicate_negative = 0

    for pair_key, labels in pair_labels.items():

        if len(labels) > 1:
            conflicts.append(pair_key)

        positive_count = pair_counts.get(
            (pair_key, 1),
            0,
        )

        negative_count = pair_counts.get(
            (pair_key, 0),
            0,
        )

        if positive_count > 1:
            duplicate_positive += positive_count - 1

        if negative_count > 1:
            duplicate_negative += negative_count - 1

    print("#" * 70)
    print("TRAINING DATA QUALITY REPORT")
    print("#" * 70)

    print(
        f"Duplicate positive rows: "
        f"{duplicate_positive}"
    )

    print(
        f"Duplicate negative rows: "
        f"{duplicate_negative}"
    )

    print(
        f"Cross-label conflicts: "
        f"{len(conflicts)}"
    )

    if conflicts:
        print("\nFirst 10 conflicts:\n")

        for hotel_id, room_a, room_b in conflicts[:10]:
            print("-" * 60)
            print("Hotel ID:", hotel_id)
            print("Room A:", room_a)
            print("Room B:", room_b)
            print(
                "Labels:",
                pair_labels[(hotel_id, room_a, room_b)],
            )


if __name__ == "__main__":
    check_training_dataset()