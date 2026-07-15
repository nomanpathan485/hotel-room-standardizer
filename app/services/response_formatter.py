def display_text(value: str | None) -> str | None:
    if value is None:
        return None

    return value.replace("_", " ").title()

def format_beds(bed_configuration: list[dict]) -> list[dict]:
    formatted = []

    for bed in bed_configuration:
        bed_type = bed.get("type")

        if not bed_type:
            continue

        formatted.append(
            {
                "type": display_text(bed_type)
            }
        )

    return formatted

def format_category(features: dict, standard_name: str) -> str:
    room_class = features.get("room_class")
    category = features.get("category")
    suite_type = features.get("suite_type")

    if category == "suite":
        if suite_type and suite_type not in {"standard", "not_applicable"}:
            return f"{display_text(suite_type)} Suite"

        return "Suite"

    if category == "family":
        return "Family Room"

    if category == "room":
        if room_class and room_class != "unknown":
            if "guest room" in standard_name.lower():
                return f"{display_text(room_class)} Guest Room"

            return f"{display_text(room_class)} Room"

        return "Room"

    return display_text(category)

def format_bed_info(beds: list[dict]) -> str | None:
    bed_types = [
        display_text(bed.get("type"))
        for bed in beds
        if bed.get("type")
    ]

    if not bed_types:
        return None

    if len(bed_types) == 1:
        return bed_types[0]

    if len(bed_types) == 2:
        return f"{bed_types[0]} or {bed_types[1]}"

    return ", ".join(bed_types)


def format_grouped_response(groups: list[dict]) -> dict:
    standard_rooms = []

    for group in groups:
        first_room = group["rooms"][0]
        features = first_room["features"]

        mapped_room_rates = []

        for room in group["rooms"]:
            mapped_room_rates.append(
                {
                    "inputIndex": room.get("index", room.get("id")),
                    "roomCode": room.get("code"),
                    "boardBasis": room.get("board_basis"),
                    "refundability": "Unknown",
                    "isDefault": False,
                    "matchScore": 100,
                    "cfs": 100,
                    "attributes": [],
                }
            )


        standard_rooms.append(
            {
                "standardName": display_text(group["standard_room_name"]),
                "category": format_category(
                    features,
                    group["standard_room_name"],
                ),
                "view": display_text(features.get("view")),
                "beds": format_beds(
                    features.get("bed_configuration", [])
                ),
                "bedInfo": format_bed_info(
                    features.get("bed_configuration", [])
                ),
                "mappedRoomRates": mapped_room_rates,
                "facilities": [],
                "attributes": [],
            }
        )

    return {"standardRooms": standard_rooms}