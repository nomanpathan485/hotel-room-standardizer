from app.services.matcher import is_match
def group_rooms(rooms):
    groups = []

    for room in rooms:
        placed = False

        for group in groups:
            for existing_room in group["rooms"]:

                if is_match(room["room_name"], existing_room["room_name"]):
                    group["rooms"].append(room)
                    placed = True
                    break

            if placed:
                break

        if not placed:
            groups.append({
            "group_id": len(groups) + 1,
            "rooms": [room]
        })
    return groups
