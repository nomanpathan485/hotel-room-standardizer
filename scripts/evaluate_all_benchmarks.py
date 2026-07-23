from app.services.dataset_store import (
    BASE_DATASET_DIR,
    load_benchmark_case,
)
from app.services.group_comparator import compare_group_outputs


def evaluate_all_benchmarks():
    case_directories = [
        path
        for path in BASE_DATASET_DIR.iterdir()
        if path.is_dir()
    ]

    if not case_directories:
        print("No benchmark cases found.")
        return

    total_vervotech_groups = 0
    total_our_groups = 0
    total_exact_matches = 0
    total_missing_indexes = 0
    total_extra_indexes = 0

    print(f"\nFound {len(case_directories)} benchmark cases.\n")

    for case_directory in sorted(case_directories):
        case_id = case_directory.name

        try:
            case = load_benchmark_case(case_id)

            comparison = compare_group_outputs(
                case["vervotech"],
                case["our_v4"],
            )

            summary = comparison["summary"]

            total_vervotech_groups += summary["total_vervotech_groups"]
            total_our_groups += summary["total_our_groups"]
            total_exact_matches += summary["exact_match_groups"]
            total_missing_indexes += summary["total_missing_indexes"]
            total_extra_indexes += summary["total_extra_indexes"]

            print("=" * 70)
            print(f"CASE: {case_id}")
            print(
                f"Exact match: "
                f"{summary['exact_match_groups']} / "
                f"{summary['total_vervotech_groups']} "
                f"({summary['exact_match_percentage']}%)"
            )
            print(
                f"Our groups: {summary['total_our_groups']}"
            )
            print(
                f"Missing indexes: "
                f"{summary['total_missing_indexes']}"
            )
            print(
                f"Extra indexes: "
                f"{summary['total_extra_indexes']}"
            )

        except Exception as error:
            print("=" * 70)
            print(f"FAILED: {case_id}")
            print(f"Error: {error}")

    if total_vervotech_groups > 0:
        overall_exact_percentage = round(
            (
                total_exact_matches
                / total_vervotech_groups
            )
            * 100,
            2,
        )
    else:
        overall_exact_percentage = 0.0

    print("\n")
    print("#" * 70)
    print("OVERALL V4 BENCHMARK RESULT")
    print("#" * 70)

    print(
        f"Hotels tested: {len(case_directories)}"
    )
    print(
        f"Total Vervotech groups: "
        f"{total_vervotech_groups}"
    )
    print(
        f"Total our groups: "
        f"{total_our_groups}"
    )
    print(
        f"Total exact groups: "
        f"{total_exact_matches}"
    )
    print(
        f"Overall exact match percentage: "
        f"{overall_exact_percentage}%"
    )
    print(
        f"Total missing indexes: "
        f"{total_missing_indexes}"
    )
    print(
        f"Total extra indexes: "
        f"{total_extra_indexes}"
    )


if __name__ == "__main__":
    evaluate_all_benchmarks()