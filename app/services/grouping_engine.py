from app.services.matcher import is_match
from app.services.feature_extractor import extract_features
from app.services.normalizer import normalize_room_name
from app.services.llm import generate_canonical_name


def group_rooms(rooms, generate_standard_name : bool = False):
    groups = []

    for room in rooms:
        room_with_features = {
            **room,
            "normalized_name": normalize_room_name(room["room_name"]),
            "features": extract_features(room["room_name"]),
        }

        placed = False

        for group in groups:
            representative_room = group["rooms"][0]
            
            if is_match(room_with_features, representative_room):
                group["rooms"].append(room_with_features)
                placed = True
                break

            if placed:
                break

        if not placed:
            groups.append(
                {
                    "group_id": len(groups) + 1,
                    "rooms": [room_with_features],
                }
            )

    final_groups = []

    for group in groups:
        room_names = [
            room["room_name"]
            for room in group["rooms"]
        ]

        if generate_standard_name:
            existing_names = {
                room.get("standard_room_name")
                for room in group["rooms"]
                if room.get("standard_room_name")
            }

            if len(existing_names) == 1:
                standard_room_name = next(iter(existing_names))
            else:
                standard_room_name = generate_canonical_name(room_names)
        else:
            standard_room_name = min(
                room["normalized_name"]
                for room in group["rooms"]
            )

        final_groups.append(
            {
                "group_id": group["group_id"],
                "standard_room_name": standard_room_name,
                "rooms": group["rooms"],
            }
        )

    return final_groups