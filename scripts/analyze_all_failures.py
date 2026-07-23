from collections import Counter

from app.services.dataset_store import (
    BASE_DATASET_DIR,
    load_benchmark_case,
)
from app.services.group_comparator import (
    diagnose_false_splits,
    diagnose_wrong_merges,
)


def analyze_all_failures():
    case_directories = [
        path
        for path in BASE_DATASET_DIR.iterdir()
        if path.is_dir()
    ]

    false_split_reasons = Counter()
    wrong_merge_reasons = Counter()

    total_wrong_merges = 0

    for case_directory in sorted(case_directories):
        case_id = case_directory.name

        try:
            case = load_benchmark_case(case_id)

            false_split_result = diagnose_false_splits(
                case["input"],
                case["vervotech"],
            )

            wrong_merge_result = diagnose_wrong_merges(
                case["input"],
                case["vervotech"],
                case["our_v4"],
            )

            # Aggregate false-split rejection reasons
            rejection_summary = false_split_result.get(
                "rejection_summary",
                {},
            )

            for reason, count in rejection_summary.items():
                false_split_reasons[reason] += count

            # Aggregate wrong-merge acceptance reasons
            wrong_merge_diagnostics = wrong_merge_result.get(
                "wrong_merge_diagnostics",
                [],
            )

            total_wrong_merges += wrong_merge_result.get(
                "wrong_merge_count",
                0,
            )

            for merge in wrong_merge_diagnostics:
                accepted_by = merge.get(
                    "accepted_by",
                    "unknown",
                )

                wrong_merge_reasons[accepted_by] += 1

            print(f"Analyzed: {case_id}")

        except Exception as error:
            print(f"FAILED: {case_id}")
            print(f"Error: {error}")

    print("\n")
    print("#" * 70)
    print("FALSE SPLIT REASONS")
    print("#" * 70)

    for reason, count in false_split_reasons.most_common():
        print(f"{reason}: {count}")

    print("\n")
    print("#" * 70)
    print("WRONG MERGE REASONS")
    print("#" * 70)

    for reason, count in wrong_merge_reasons.most_common():
        print(f"{reason}: {count}")

    print("\n")
    print(f"Total diagnosed wrong merges: {total_wrong_merges}")


if __name__ == "__main__":
    analyze_all_failures()