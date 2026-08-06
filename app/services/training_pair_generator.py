from itertools import combinations
from app.services.normalizer import normalize_room_name
from rapidfuzz.fuzz import token_set_ratio
import random


HARD_NEGATIVE_THRESHOLD = 70
EASY_NEGATIVE_MAX_PER_CASE = 50


def get_rooms_by_index(input_data: dict) -> dict:
    rooms_by_index = {}

    for room in input_data.get("roomRates", []):
        room_index = room.get("index")

        if room_index is not None:
            rooms_by_index[room_index] = room

    return rooms_by_index


def generate_positive_pairs(
    input_data: dict,
    vervotech_response: dict,
) -> list[dict]:

    rooms_by_index = get_rooms_by_index(input_data)
    positive_pairs = []

    for group in vervotech_response.get("standardRooms", []):
        indexes = [
            mapped_room.get("inputIndex")
            for mapped_room in group.get("mappedRoomRates", [])
            if mapped_room.get("inputIndex") is not None
        ]

        for index_a, index_b in combinations(indexes, 2):
            room_a = rooms_by_index.get(index_a)
            room_b = rooms_by_index.get(index_b)

            if room_a is None or room_b is None:
                continue

            positive_pairs.append(
                {
                    "room_a_index": index_a,
                    "room_a_name": room_a.get("roomName", ""),
                    "room_b_index": index_b,
                    "room_b_name": room_b.get("roomName", ""),
                    "label": 1,
                }
            )

    return positive_pairs


def generate_hard_negative_pairs(
    input_data: dict,
    vervotech_response: dict,
    threshold: int = HARD_NEGATIVE_THRESHOLD,
) -> list[dict]:

    rooms_by_index = get_rooms_by_index(input_data)

    groups = []

    for group in vervotech_response.get("standardRooms", []):
        indexes = [
            mapped_room.get("inputIndex")
            for mapped_room in group.get("mappedRoomRates", [])
            if mapped_room.get("inputIndex") is not None
        ]

        groups.append(indexes)

    hard_negative_pairs = []

    for group_a, group_b in combinations(groups, 2):
        for index_a in group_a:
            for index_b in group_b:
                room_a = rooms_by_index.get(index_a)
                room_b = rooms_by_index.get(index_b)

                if room_a is None or room_b is None:
                    continue

                room_a_name = room_a.get("roomName", "")
                room_b_name = room_b.get("roomName", "")

                normalized_a = normalize_room_name(room_a_name)
                normalized_b = normalize_room_name(room_b_name)

                if normalized_a == normalized_b:
                    continue


                score = token_set_ratio(
                    normalized_a,
                    normalized_b,
                )
                if score >= threshold:
                    hard_negative_pairs.append(
                        {
                            "room_a_index": index_a,
                            "room_a_name": room_a_name,
                            "room_b_index": index_b,
                            "room_b_name": room_b_name,
                            "fuzzy_score": round(score, 2),
                            "label": 0,
                        }
                    )

    return hard_negative_pairs
def generate_easy_negative_pairs(
    input_data: dict,
    vervotech_response: dict,
    threshold: int = HARD_NEGATIVE_THRESHOLD,
    max_pairs: int = EASY_NEGATIVE_MAX_PER_CASE,
    seed: int = 42,
) -> list[dict]:

    rooms_by_index = get_rooms_by_index(input_data)

    groups = []

    for group in vervotech_response.get("standardRooms", []):
        indexes = [
            mapped_room.get("inputIndex")
            for mapped_room in group.get("mappedRoomRates", [])
            if mapped_room.get("inputIndex") is not None
        ]

        groups.append(indexes)

    random_generator = random.Random(seed)
    sampled_pairs = []
    eligible_pair_count = 0

    for group_a, group_b in combinations(groups, 2):
        for index_a in group_a:
            for index_b in group_b:
                room_a = rooms_by_index.get(index_a)
                room_b = rooms_by_index.get(index_b)

                if room_a is None or room_b is None:
                    continue

                room_a_name = room_a.get("roomName", "")
                room_b_name = room_b.get("roomName", "")

                normalized_a = normalize_room_name(room_a_name)
                normalized_b = normalize_room_name(room_b_name)

                if not normalized_a or not normalized_b:
                    continue

                if normalized_a == normalized_b:
                    continue

                score = token_set_ratio(
                    normalized_a,
                    normalized_b,
                )

                if score >= threshold:
                    continue

                easy_negative = {
                    "room_a_index": index_a,
                    "room_a_name": room_a_name,
                    "room_b_index": index_b,
                    "room_b_name": room_b_name,
                    "fuzzy_score": round(score, 2),
                    "label": 0,
                }

                eligible_pair_count += 1

                if len(sampled_pairs) < max_pairs:
                    sampled_pairs.append(easy_negative)
                    continue

                replacement_index = random_generator.randint(
                    0,
                    eligible_pair_count - 1,
                )

                if replacement_index < max_pairs:
                    sampled_pairs[replacement_index] = easy_negative

    return sampled_pairs


def deduplicate_pairs(
    pairs: list[dict],
) -> list[dict]:

    unique_pairs = []
    seen = set()

    for pair in pairs:
        room_a = pair["room_a_name"].strip().lower()
        room_b = pair["room_b_name"].strip().lower()

        pair_key = tuple(
            sorted([room_a, room_b])
        )

        if pair_key in seen:
            continue

        seen.add(pair_key)
        unique_pairs.append(pair)

    return unique_pairs