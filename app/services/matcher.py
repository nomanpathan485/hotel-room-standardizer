from rapidfuzz import fuzz


def _same_view(view_a: str, view_b: str) -> bool:
    # "(No View)" / "No View" is supplier noise; treat it as transparent
    # so a "Garden View (No View)" room can still match a plain "Garden
    # View" room.
    if view_a == "no_view" or view_b == "no_view":
        return True
    return view_a == view_b


def _same_bed_configuration(config_a: list, config_b: list) -> bool:
    # Only meaningful when both sides actually describe a bed layout.
    # When one side is empty (older supplier names that omit the
    # breakdown), fall back to the bed_type / fuzzy check.
    if not config_a or not config_b:
        return True
    return config_a == config_b

def get_bed_signature(features: dict) -> set[tuple[str, int | None]]:
    return {
        (bed["type"], bed.get("count"))
        for bed in features.get("bed_configuration", [])
    }


def is_match(room_a, room_b, threshold=90):
    normalized_a = room_a["normalized_name"]
    normalized_b = room_b["normalized_name"]

    # Exact match
    if normalized_a == normalized_b:
        return True

    # Extract features
    features_a = room_a["features"]
    features_b = room_b["features"]

    bed_signature_a = get_bed_signature(features_a)
    bed_signature_b = get_bed_signature(features_b)

    category_a = features_a["category"]
    category_b = features_b["category"]

    room_class_a = features_a["room_class"]
    room_class_b = features_b["room_class"]

    suite_type_a = features_a["suite_type"]
    suite_type_b = features_b["suite_type"]

    bedroom_count_a = features_a["bedroom_count"]
    bedroom_count_b = features_b["bedroom_count"]

    club_access_a = features_a["club_access"]
    club_access_b = features_b["club_access"]

    view_a = features_a["view"]
    view_b = features_b["view"]

    balcony_a = features_a["balcony"]
    balcony_b = features_b["balcony"]

    terrace_a = features_a.get("terrace", False)
    terrace_b = features_b.get("terrace", False)

    bed_count_a = features_a["dormitory_bed_count"]
    bed_count_b = features_b["dormitory_bed_count"]

    dormitory_type_a = features_a["dormitory_type"]
    dormitory_type_b = features_b["dormitory_type"]

    bed_configuration_a = features_a.get("bed_configuration", [])
    bed_configuration_b = features_b.get("bed_configuration", [])

    # Different room categories
    if category_a != category_b:
        return False

    if room_class_a != room_class_b:
        return False
    if suite_type_a != suite_type_b:
        return False
    if bedroom_count_a != bedroom_count_b:
        return False
    if club_access_a != club_access_b:
        return False

    # Dormitory rule
    if category_a == "dormitory":
        if bed_count_a is None or bed_count_b is None:
            return False

        if bed_count_a != bed_count_b:
            return False

        if (
            dormitory_type_a != "unknown"
            and dormitory_type_b != "unknown"
            and dormitory_type_a != dormitory_type_b
        ):
            return False

        return True

    # Different views (no_view is treated as transparent supplier noise)
    if not _same_view(view_a, view_b):
        return False

    # Balcony / terrace mismatch. has_balcony already treats "terrace"
    # as a balcony, so this catches "garden view + balcony" rooms vs
    # "garden view + no balcony" rooms. The standalone terrace check
    # catches a room that explicitly has a terrace vs one that doesn't.
    if balcony_a != balcony_b:
        return False
    if terrace_a != terrace_b:
        return False

    bed_type_a = features_a["bed_type"]
    bed_type_b = features_b["bed_type"]

    if bed_type_a != bed_type_b:
        return False

    # Bed configuration: only reject when both sides actually specify one
    # and they disagree. Empty lists fall through to bed_type / fuzzy.
    if not _same_bed_configuration(bed_configuration_a, bed_configuration_b):
        return False
    
    if bed_signature_a and bed_signature_b:
        if bed_signature_a != bed_signature_b:
            return False

    # Final fuzzy comparison
    score = fuzz.token_set_ratio(normalized_a, normalized_b)

    return score >= threshold