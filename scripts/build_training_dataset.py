import csv

from app.services.dataset_store import (
    BASE_DATASET_DIR,
    load_benchmark_case,
)
from app.services.training_pair_generator import (
    deduplicate_pairs,
    generate_easy_negative_pairs,
    generate_hard_negative_pairs,
    generate_positive_pairs,
)


OUTPUT_FILE = "data/training_pairs.csv"


def extract_hotel_id(case_id: str) -> str:
    parts = case_id.split("_")

    if len(parts) >= 2:
        return parts[1]

    return "unknown"

def remove_cross_label_conflicts(pairs: list[dict]) -> list[dict]:
    pair_labels = {}

    for pair in pairs:
        room_a = pair["room_a_name"].strip().lower()
        room_b = pair["room_b_name"].strip().lower()

        name_pair = tuple(sorted([room_a, room_b]))

        pair_key = (
            pair["hotel_id"],
            *name_pair,
        )

        pair_labels.setdefault(pair_key, set()).add(
            pair["label"]
        )

    cleaned_pairs = []

    for pair in pairs:
        room_a = pair["room_a_name"].strip().lower()
        room_b = pair["room_b_name"].strip().lower()

        name_pair = tuple(sorted([room_a, room_b]))

        pair_key = (
            pair["hotel_id"],
            *name_pair,
        )

        if len(pair_labels[pair_key]) > 1:
            continue

        cleaned_pairs.append(pair)

    return cleaned_pairs


def build_training_dataset():
    all_pairs = []

    case_directories = [
        path
        for path in BASE_DATASET_DIR.iterdir()
        if path.is_dir()
    ]

    print(f"Found {len(case_directories)} benchmark cases.\n")

    for case_directory in sorted(case_directories):
        case_id = case_directory.name
        hotel_id = extract_hotel_id(case_id)

        try:
            case = load_benchmark_case(case_id)

            raw_positive_pairs = generate_positive_pairs(
                input_data=case["input"],
                vervotech_response=case["vervotech"],
            )

            positive_pairs = deduplicate_pairs(
                raw_positive_pairs
            )
            raw_easy_negative_pairs = generate_easy_negative_pairs(
                input_data=case["input"],
                vervotech_response=case["vervotech"],
            )

            easy_negative_pairs = deduplicate_pairs(
                raw_easy_negative_pairs
            )

            raw_negative_pairs = generate_hard_negative_pairs(
                input_data=case["input"],
                vervotech_response=case["vervotech"],
            )

            negative_pairs = deduplicate_pairs(
                raw_negative_pairs
            )

            for pair in positive_pairs:
                all_pairs.append(
                    {
                        "case_id": case_id,
                        "hotel_id": hotel_id,
                        "room_a_index": pair["room_a_index"],
                        "room_b_index": pair["room_b_index"],
                        "room_a_name": pair["room_a_name"],
                        "room_b_name": pair["room_b_name"],
                        "fuzzy_score": "",
                        "label": 1,
                    }
                )

            for pair in negative_pairs:
                all_pairs.append(
                    {
                        "case_id": case_id,
                        "hotel_id": hotel_id,
                        "room_a_index": pair["room_a_index"],
                        "room_b_index": pair["room_b_index"],
                        "room_a_name": pair["room_a_name"],
                        "room_b_name": pair["room_b_name"],
                        "fuzzy_score": pair.get(
                            "fuzzy_score",
                            "",
                        ),
                        "label": 0,
                    }
                )
            for pair in easy_negative_pairs:
                all_pairs.append(
                    {
                        "case_id": case_id,
                        "hotel_id": hotel_id,
                        "room_a_index": pair["room_a_index"],
                        "room_b_index": pair["room_b_index"],
                        "room_a_name": pair["room_a_name"],
                        "room_b_name": pair["room_b_name"],
                        "fuzzy_score": pair["fuzzy_score"],
                        "label": 0,
                    }
                )

            print(
                f"{case_id}: "
                f"{len(positive_pairs)} positive, "
                f"{len(negative_pairs)} hard negative, "
                f"{len(easy_negative_pairs)} easy negative"
            )
        except Exception as error:
            print(f"FAILED: {case_id}")
            print(f"Error: {error}")

    all_pairs = remove_cross_label_conflicts(all_pairs)
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        fieldnames = [
            "case_id",
            "hotel_id",
            "room_a_index",
            "room_b_index",
            "room_a_name",
            "room_b_name",
            "fuzzy_score",
            "label",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(all_pairs)

    positive_count = sum(
        1
        for pair in all_pairs
        if pair["label"] == 1
    )

    negative_count = sum(
        1
        for pair in all_pairs
        if pair["label"] == 0
    )
    hard_negative_count = sum(
        1
        for pair in all_pairs
        if pair["label"] == 0
        and float(pair["fuzzy_score"]) >= 70
    )

    easy_negative_count = sum(
        1
        for pair in all_pairs
        if pair["label"] == 0
        and float(pair["fuzzy_score"]) < 70
    )

    print("\n")
    print("#" * 70)
    print("TRAINING DATASET CREATED")
    print("#" * 70)

    print(f"Total pairs: {len(all_pairs)}")
    print(f"Positive pairs: {positive_count}")
    print(f"Negative pairs: {negative_count}")
    print(f"Hard negative pairs: {hard_negative_count}")
    print(f"Easy negative pairs: {easy_negative_count}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_training_dataset()