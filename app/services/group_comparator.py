def extract_index_set(group: dict) -> set[int]:
    return {
        room["inputIndex"]
        for room in group.get("mappedRoomRates", [])
    }


def compare_group_outputs(
    vervotech_response: dict,
    our_response: dict,
) -> list[dict]:
    vervotech_groups = vervotech_response.get("standardRooms", [])
    our_groups = our_response.get("standardRooms", [])

    results = []

    for vervotech_group in vervotech_groups:
        expected_indexes = extract_index_set(vervotech_group)

        best_match = None
        best_score = 0

        for our_group in our_groups:
            actual_indexes = extract_index_set(our_group)

            intersection = len(expected_indexes & actual_indexes)
            union = len(expected_indexes | actual_indexes)

            score = intersection / union if union else 0

            if score > best_score:
                best_score = score
                best_match = our_group

        if best_match is None:
            results.append(
                {
                    "vervotech_name": vervotech_group.get("standardName"),
                    "our_name": None,
                    "missing_indexes": sorted(expected_indexes),
                    "extra_indexes": [],
                    "exact_match": False,
                }
            )
            continue

        actual_indexes = extract_index_set(best_match)

        results.append(
            {
                "vervotech_name": vervotech_group.get("standardName"),
                "our_name": best_match.get("standardName"),
                "expected_count": len(expected_indexes),
                "actual_count": len(actual_indexes),
                "common_count": len(expected_indexes & actual_indexes),
                "missing_indexes": sorted(expected_indexes - actual_indexes),
                "extra_indexes": sorted(actual_indexes - expected_indexes),
                "exact_match": expected_indexes == actual_indexes,
            }
        )

    return results