from rapidfuzz import process, fuzz

from app.services.normalizer import normalize_room_name


def find_best_match(query, choices):
    # Normalize the query
    normalized_query = normalize_room_name(query)

    # Map normalized names back to their original names
    normalized_map = {
        normalize_room_name(choice): choice
        for choice in choices
    }

    # Search using normalized names
    match = process.extractOne(
        normalized_query,
        list(normalized_map.keys()),
        scorer=fuzz.token_set_ratio
    )

    # Return the original room name instead of the normalized one
    original_room = normalized_map[match[0]]

    return original_room, match[1]

def is_match(room_a, room_b, threshold=90):
    room_a = normalize_room_name(room_a)
    room_b = normalize_room_name(room_b)

    score = fuzz.token_set_ratio(room_a, room_b)

    return score >= threshold