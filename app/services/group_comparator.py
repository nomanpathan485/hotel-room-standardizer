from collections import Counter

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

    results = []

    exact_match_count = 0
    total_missing_indexes = 0
    total_extra_indexes = 0

    for vervotech_group in vervotech_groups:
        expected_indexes = extract_index_set(vervotech_group)

        best_match = None
        best_score = 0.0

        for our_group in our_groups:
            actual_indexes = extract_index_set(our_group)

            intersection = len(
                expected_indexes & actual_indexes
            )

            union = len(
                expected_indexes | actual_indexes
            )

            score = (
                intersection / union
                if union
                else 0.0
            )

            if score > best_score:
                best_score = score
                best_match = our_group

        if best_match is None:
            missing_indexes = sorted(expected_indexes)

            total_missing_indexes += len(
                missing_indexes
            )

            results.append(
                {
                    "vervotech_name": vervotech_group.get(
                        "standardName"
                    ),
                    "our_name": None,
                    "expected_count": len(
                        expected_indexes
                    ),
                    "actual_count": 0,
                    "common_count": 0,
                    "missing_indexes": missing_indexes,
                    "extra_indexes": [],
                    "exact_match": False,
                }
            )

            continue

        actual_indexes = extract_index_set(
            best_match
        )

        missing_indexes = sorted(
            expected_indexes - actual_indexes
        )

        extra_indexes = sorted(
            actual_indexes - expected_indexes
        )

        exact_match = (
            expected_indexes == actual_indexes
        )

        if exact_match:
            exact_match_count += 1

        total_missing_indexes += len(
            missing_indexes
        )

        total_extra_indexes += len(
            extra_indexes
        )

        results.append(
            {
                "vervotech_name": vervotech_group.get(
                    "standardName"
                ),
                "our_name": best_match.get(
                    "standardName"
                ),
                "expected_count": len(
                    expected_indexes
                ),
                "actual_count": len(
                    actual_indexes
                ),
                "common_count": len(
                    expected_indexes
                    & actual_indexes
                ),
                "missing_indexes": missing_indexes,
                "extra_indexes": extra_indexes,
                "exact_match": exact_match,
            }
        )

    total_groups = len(
        vervotech_groups
    )

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
        "total_missing_indexes": (
            total_missing_indexes
        ),
        "total_extra_indexes": (
            total_extra_indexes
        ),
    }

    return {
        "summary": summary,
        "groups": results,
    }

def diagnose_false_splits(
    input_data: dict,
    vervotech_response: dict,
) -> dict:
    room_rates = input_data.get("roomRates", [])
    vervotech_groups = vervotech_response.get("standardRooms", [])

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

    rejection_counts = Counter()
    diagnostics = []

    for group in vervotech_groups:
        indexes = [
            room.get("inputIndex")
            for room in group.get("mappedRoomRates", [])
        ]

        valid_rooms = [
            rooms_by_index[index]
            for index in indexes
            if index in rooms_by_index
        ]

        if len(valid_rooms) < 2:
            continue

        representative = valid_rooms[0]

        for candidate in valid_rooms[1:]:
            result = diagnose_match(
                representative,
                candidate,
            )

            if result["matched"]:
                continue

            reason = result["reason"]

            rejection_counts[reason] += 1

            diagnostics.append(
                {
                    "vervotech_group": group.get("standardName"),
                    "representative_index": representative.get("index"),
                    "representative_name": representative.get("roomName"),
                    "candidate_index": candidate.get("index"),
                    "candidate_name": candidate.get("roomName"),
                    "rejected_by": reason,
                    "details": result,
                }
            )

    return {
        "rejection_summary": dict(
            rejection_counts.most_common()
        ),
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

            result = diagnose_match_v4(
                representative,
                candidate,
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
                    "accepted_by": result.get("reason"),
                    "details": result,
                }
            )

    return {
        "wrong_merge_count": len(wrong_merges),
        "wrong_merge_diagnostics": wrong_merges,
    }