from collections import Counter
from app.services.matcher import (
    MatchDecision,
    decide_room_match_ml,
)

from app.services.feature_extractor import extract_features
from app.services.matcher import (
    diagnose_match,
    diagnose_match_v4,
)
from app.services.normalizer import normalize_room_name



def extract_index_set(group: dict) -> set[int]:
    return {
        room["inputIndex"]
        for room in group.get("mappedRoomRates", [])
    }

def compare_group_outputs(
    vervotech_response: dict,
    our_response: dict,
) -> dict:
    vervotech_groups = vervotech_response.get("standardRooms", [])
    our_groups = our_response.get("standardRooms", [])

    expected_group_sets = [
        extract_index_set(group)
        for group in vervotech_groups
    ]
    actual_group_sets = [
        extract_index_set(group)
        for group in our_groups
    ]

    all_expected_indexes = set().union(
        *expected_group_sets
    ) if expected_group_sets else set()
    all_actual_indexes = set().union(
        *actual_group_sets
    ) if actual_group_sets else set()

    globally_missing_indexes = sorted(
        all_expected_indexes - all_actual_indexes
    )
    globally_extra_indexes = sorted(
        all_actual_indexes - all_expected_indexes
    )

    results = []
    exact_match_count = 0
    split_group_count = 0

    for vervotech_group_index, vervotech_group in enumerate(
        vervotech_groups
    ):
        expected_indexes = expected_group_sets[
            vervotech_group_index
        ]
        overlapping_our_groups = []
        covered_expected_indexes = set()
        exact_match = False

        for our_group_index, our_group in enumerate(our_groups):
            actual_indexes = actual_group_sets[our_group_index]
            common_indexes = expected_indexes & actual_indexes

            if not common_indexes:
                continue

            covered_expected_indexes.update(common_indexes)

            union = expected_indexes | actual_indexes
            jaccard_score = (
                len(common_indexes) / len(union)
                if union
                else 0.0
            )

            group_is_exact = expected_indexes == actual_indexes
            exact_match = exact_match or group_is_exact

            overlapping_our_groups.append(
                {
                    "our_group_index": our_group_index,
                    "our_name": our_group.get("standardName"),
                    "our_group_count": len(actual_indexes),
                    "common_count": len(common_indexes),
                    "common_indexes": sorted(common_indexes),
                    "indexes_from_other_vervotech_groups": sorted(
                        actual_indexes - expected_indexes
                    ),
                    "jaccard_score": round(jaccard_score, 3),
                    "exact_match": group_is_exact,
                }
            )

        overlapping_our_groups.sort(
            key=lambda group: (
                group["common_count"],
                group["jaccard_score"],
            ),
            reverse=True,
        )

        split_across_our_groups = len(overlapping_our_groups) > 1

        if split_across_our_groups:
            split_group_count += 1

        if exact_match:
            exact_match_count += 1

        results.append(
            {
                "vervotech_group_index": vervotech_group_index,
                "vervotech_name": vervotech_group.get("standardName"),
                "expected_count": len(expected_indexes),
                "expected_indexes": sorted(expected_indexes),
                "overlapping_our_group_count": len(
                    overlapping_our_groups
                ),
                "overlapping_our_groups": overlapping_our_groups,
                "indexes_absent_from_our_output": sorted(
                    expected_indexes - covered_expected_indexes
                ),
                "split_across_our_groups": split_across_our_groups,
                "exact_match": exact_match,
            }
        )

    merged_our_groups = []

    for our_group_index, our_group in enumerate(our_groups):
        actual_indexes = actual_group_sets[our_group_index]
        overlapping_vervotech_groups = []

        for vervotech_group_index, vervotech_group in enumerate(
            vervotech_groups
        ):
            expected_indexes = expected_group_sets[
                vervotech_group_index
            ]
            common_indexes = actual_indexes & expected_indexes

            if not common_indexes:
                continue

            overlapping_vervotech_groups.append(
                {
                    "vervotech_group_index": vervotech_group_index,
                    "vervotech_name": vervotech_group.get("standardName"),
                    "common_count": len(common_indexes),
                    "common_indexes": sorted(common_indexes),
                }
            )

        if len(overlapping_vervotech_groups) > 1:
            merged_our_groups.append(
                {
                    "our_group_index": our_group_index,
                    "our_name": our_group.get("standardName"),
                    "our_group_count": len(actual_indexes),
                    "overlapping_vervotech_groups": (
                        overlapping_vervotech_groups
                    ),
                }
            )

    total_groups = len(vervotech_groups)

    exact_match_percentage = (
        (
            exact_match_count
            / total_groups
        )
        * 100
        if total_groups
        else 0.0
    )

    summary = {
        "total_vervotech_groups": total_groups,
        "total_our_groups": len(
            our_groups
        ),
        "exact_match_groups": exact_match_count,
        "exact_match_percentage": round(
            exact_match_percentage,
            2,
        ),
        "vervotech_groups_split_across_our_groups": split_group_count,
        "our_groups_merging_vervotech_groups": len(merged_our_groups),
        "globally_missing_index_count": len(globally_missing_indexes),
        "globally_missing_indexes": globally_missing_indexes,
        "globally_extra_index_count": len(globally_extra_indexes),
        "globally_extra_indexes": globally_extra_indexes,
    }

    return {
        "summary": summary,
        "groups": results,
        "merged_our_groups": merged_our_groups,
    }

def diagnose_false_splits(
    input_data: dict,
    vervotech_response: dict,
    our_response: dict,
) -> dict:
    room_rates = input_data.get("roomRates", [])
    vervotech_groups = vervotech_response.get("standardRooms", [])
    our_groups = our_response.get("standardRooms", [])

    rooms_by_index = {}

    for room in room_rates:
        index = room.get("index")

        if index is None:
            continue

        room_name = room.get("roomName", "")

        rooms_by_index[index] = {
            **room,
            "room_name": room_name,
            "normalized_name": normalize_room_name(room_name),
            "features": extract_features(room_name),
        }

    # Find which of our groups contains each room.
    our_group_by_index = {}

    for group_position, group in enumerate(our_groups):
        for room in group.get("mappedRoomRates", []):
            input_index = room.get("inputIndex")

            if input_index is None:
                continue

            our_group_by_index[input_index] = {
                "group_position": group_position,
                "standard_name": group.get("standardName"),
            }

    rejection_counts = Counter()
    diagnostics = []

    for vervotech_group in vervotech_groups:
        indexes = [
            room.get("inputIndex")
            for room in vervotech_group.get("mappedRoomRates", [])
        ]

        valid_rooms = [
            rooms_by_index[index]
            for index in indexes
            if (
                index in rooms_by_index
                and index in our_group_by_index
            )
        ]

        if len(valid_rooms) < 2:
            continue

        # Partition Vervotech's group according to our groups.
        partitions = {}

        for room in valid_rooms:
            our_group = our_group_by_index[room["index"]]
            group_position = our_group["group_position"]

            partitions.setdefault(group_position, []).append(room)

        # Our engine did not split this Vervotech group.
        if len(partitions) < 2:
            continue

        # Use the largest of our partitions as the reference group.
        reference_partition = max(
            partitions.values(),
            key=len,
        )
        representative = reference_partition[0]
        representative_group = our_group_by_index[
            representative["index"]
        ]

        for group_position, partition_rooms in partitions.items():
            if partition_rooms is reference_partition:
                continue

            for candidate in partition_rooms:
                decision = decide_room_match_ml(
                    representative,
                    candidate,
                    probability_threshold=0.85,
                )

                result = {
                    "decision": decision.value,
                    "matched": decision == MatchDecision.MATCH,
                }

                if decision == MatchDecision.MATCH:
                    reason = "selected_pair_matches_but_groups_differ"
                elif decision == MatchDecision.UNCERTAIN:
                    reason = "ml_matcher_uncertain"
                else:
                    reason = "ml_matcher_no_match"

                rejection_counts[reason] += 1

                diagnostics.append(
                    {
                        "vervotech_group": (
                            vervotech_group.get("standardName")
                        ),
                        "representative": {
                            "index": representative.get("index"),
                            "room_name": representative.get("roomName"),
                            "our_group": representative_group[
                                "standard_name"
                            ],
                        },
                        "candidate": {
                            "index": candidate.get("index"),
                            "room_name": candidate.get("roomName"),
                            "our_group": our_group_by_index[
                                candidate["index"]
                            ]["standard_name"],
                        },
                        "reason": reason,
                        "match_details": result,
                    }
                )

    return {
        "rejection_summary": dict(
            rejection_counts.most_common()
        ),
        "false_split_count": len(diagnostics),
        "false_split_diagnostics": diagnostics,
    }

def diagnose_wrong_merges(
    input_data: dict,
    vervotech_response: dict,
    our_response: dict,
) -> dict:
    room_rates = input_data.get("roomRates", [])
    vervotech_groups = vervotech_response.get("standardRooms", [])
    our_groups = our_response.get("standardRooms", [])

    rooms_by_index = {}

    for room in room_rates:
        index = room.get("index")

        if index is None:
            continue

        room_name = room.get("roomName", "")

        rooms_by_index[index] = {
            **room,
            "room_name": room_name,
            "normalized_name": normalize_room_name(room_name),
            "features": extract_features(room_name),
        }

    # Map every inputIndex to its correct Vervotech group name
    vervotech_group_by_index = {}

    for group in vervotech_groups:
        group_name = group.get("standardName")

        for room in group.get("mappedRoomRates", []):
            index = room.get("inputIndex")

            if index is not None:
                vervotech_group_by_index[index] = group_name

    wrong_merges = []

    for our_group in our_groups:
        indexes = [
            room.get("inputIndex")
            for room in our_group.get("mappedRoomRates", [])
            if room.get("inputIndex") is not None
        ]

        if len(indexes) < 2:
            continue

        representative_index = indexes[0]
        representative = rooms_by_index.get(representative_index)

        if representative is None:
            continue

        representative_correct_group = (
            vervotech_group_by_index.get(representative_index)
        )

        for candidate_index in indexes[1:]:
            candidate = rooms_by_index.get(candidate_index)

            if candidate is None:
                continue

            candidate_correct_group = (
                vervotech_group_by_index.get(candidate_index)
            )

            # Same Vervotech group means this merge is correct
            if (
                representative_correct_group
                == candidate_correct_group
            ):
                continue

            ml_decision = decide_room_match_ml(
                representative,
                candidate,
                probability_threshold=0.85,
            )

            wrong_merges.append(
                {
                    "our_group": our_group.get("standardName"),
                    "representative_index": representative_index,
                    "representative_name": representative.get("roomName"),
                    "representative_vervotech_group": (
                        representative_correct_group
                    ),
                    "candidate_index": candidate_index,
                    "candidate_name": candidate.get("roomName"),
                    "candidate_vervotech_group": (
                        candidate_correct_group
                    ),
                    "ml_decision": ml_decision.value,
                    "details": {
                        "matched": ml_decision == MatchDecision.MATCH,
                        "decision": ml_decision.value,
                        "probability_threshold": 0.85,
},
                }
            )

    return {
        "wrong_merge_count": len(wrong_merges),
        "wrong_merge_diagnostics": wrong_merges,
    }