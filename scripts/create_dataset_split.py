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

    split_ratios = {
        "train": 0.70,
        "validation": 0.15,
        "test": 0.15,
    }

    total_pairs = sum(
        stats["total"]
        for stats in hotel_stats.values()
    )

    total_positive = sum(
        stats["positive"]
        for stats in hotel_stats.values()
    )

    total_negative = sum(
        stats["negative"]
        for stats in hotel_stats.values()
    )

    targets = {
        split_name: {
            "total": total_pairs * ratio,
            "positive": total_positive * ratio,
            "negative": total_negative * ratio,
        }
        for split_name, ratio in split_ratios.items()
    }

    random.seed(RANDOM_SEED)

    hotel_ids = list(hotel_stats.keys())
    random.shuffle(hotel_ids)

    # Large hotels are assigned first because they are
    # the hardest hotels to place without breaking balance.
    hotel_ids.sort(
        key=lambda hotel_id: hotel_stats[hotel_id]["total"],
        reverse=True,
    )

    split_hotels = {
        "train": [],
        "validation": [],
        "test": [],
    }

    split_stats = {
        split_name: {
            "total": 0,
            "positive": 0,
            "negative": 0,
        }
        for split_name in split_ratios
    }

    for hotel_id in hotel_ids:
        hotel = hotel_stats[hotel_id]

        best_split = None
        best_score = None

        for split_name in split_ratios:
            candidate_stats = {
                key: split_stats[split_name][key] + hotel[key]
                for key in ("total", "positive", "negative")
            }

            score = sum(
                (
                    candidate_stats[key]
                    / targets[split_name][key]
                ) ** 2
                for key in ("total", "positive", "negative")
            )

            if best_score is None or score < best_score:
                best_score = score
                best_split = split_name

        split_hotels[best_split].append(hotel_id)

        for key in ("total", "positive", "negative"):
            split_stats[best_split][key] += hotel[key]

    with open(
        "data/dataset_split.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            split_hotels,
            file,
            indent=4,
        )

    for split_name, hotels in split_hotels.items():
        stats = split_stats[split_name]

        print("\n" + "=" * 70)
        print(split_name.upper())
        print("=" * 70)

        for hotel_id in hotels:
            hotel = hotel_stats[hotel_id]

            print(
                f"{hotel_id} | "
                f"Positive: {hotel['positive']} | "
                f"Negative: {hotel['negative']} | "
                f"Total: {hotel['total']}"
            )

        pair_percentage = (
            stats["total"] / total_pairs * 100
        )

        positive_percentage = (
            stats["positive"] / total_positive * 100
        )

        print("-" * 70)
        print(f"Hotels: {len(hotels)}")
        print(f"Positive pairs: {stats['positive']}")
        print(f"Negative pairs: {stats['negative']}")
        print(f"Total pairs: {stats['total']}")
        print(f"Pair share: {pair_percentage:.2f}%")
        print(
            f"Positive-pair share: "
            f"{positive_percentage:.2f}%"
        )


if __name__ == "__main__":
    create_split()