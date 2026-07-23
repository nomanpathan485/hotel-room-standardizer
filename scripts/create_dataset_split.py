import csv
import json
import random
from collections import defaultdict


TRAINING_FILE = "data/training_pairs.csv"

RANDOM_SEED = 42


def get_hotel_stats():
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

    return hotel_stats


def create_split():
    hotel_stats = get_hotel_stats()

    hotel_ids = list(hotel_stats.keys())

    # Makes the random split repeatable.
    random.seed(RANDOM_SEED)
    random.shuffle(hotel_ids)

    train_hotels = hotel_ids[:10]
    validation_hotels = hotel_ids[10:12]
    test_hotels = hotel_ids[12:]

    splits = {
        "TRAIN": train_hotels,
        "VALIDATION": validation_hotels,
        "TEST": test_hotels,
    }
    split_output = {
        "train": train_hotels,
        "validation": validation_hotels,
        "test": test_hotels,
    }

    with open(
        "data/dataset_split.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            split_output,
            file,
            indent=4,
        )

    for split_name, hotels in splits.items():
        positive = sum(
            hotel_stats[hotel]["positive"]
            for hotel in hotels
        )

        negative = sum(
            hotel_stats[hotel]["negative"]
            for hotel in hotels
        )

        total = sum(
            hotel_stats[hotel]["total"]
            for hotel in hotels
        )

        print("\n" + "=" * 70)
        print(split_name)
        print("=" * 70)

        for hotel in hotels:
            stats = hotel_stats[hotel]

            print(
                f"{hotel} | "
                f"Positive: {stats['positive']} | "
                f"Negative: {stats['negative']} | "
                f"Total: {stats['total']}"
            )

        print("-" * 70)
        print(f"Hotels: {len(hotels)}")
        print(f"Positive pairs: {positive}")
        print(f"Negative pairs: {negative}")
        print(f"Total pairs: {total}")


if __name__ == "__main__":
    create_split()