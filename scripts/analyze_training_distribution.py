import csv
from collections import defaultdict


TRAINING_FILE = "data/training_pairs.csv"


def analyze_training_distribution():
    hotel_stats = defaultdict(
        lambda: {
            "positive": 0,
            "negative": 0,
            "total": 0,
        }
    )

    with open(
        TRAINING_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            hotel_id = row["hotel_id"]
            label = int(row["label"])

            hotel_stats[hotel_id]["total"] += 1

            if label == 1:
                hotel_stats[hotel_id]["positive"] += 1
            else:
                hotel_stats[hotel_id]["negative"] += 1

    sorted_hotels = sorted(
        hotel_stats.items(),
        key=lambda item: item[1]["total"],
        reverse=True,
    )

    print("#" * 70)
    print("TRAINING DATA DISTRIBUTION BY HOTEL")
    print("#" * 70)

    for hotel_id, stats in sorted_hotels:
        print(
            f"Hotel {hotel_id} | "
            f"Positive: {stats['positive']} | "
            f"Negative: {stats['negative']} | "
            f"Total: {stats['total']}"
        )


if __name__ == "__main__":
    analyze_training_distribution()