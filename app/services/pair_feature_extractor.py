from rapidfuzz.fuzz import token_set_ratio

from app.services.feature_extractor import extract_features
from app.services.normalizer import normalize_room_name
def is_known(value) -> bool:
    return value not in (
        None,
        "",
        "unknown",
    )
def has_bed_configuration(value) -> bool:
    return bool(value)

def extract_pair_features(
    room_a_name: str,
    room_b_name: str,
) -> dict:
    normalized_a = normalize_room_name(room_a_name)
    normalized_b = normalize_room_name(room_b_name)

    features_a = extract_features(room_a_name)
    features_b = extract_features(room_b_name)

    fuzzy_score = token_set_ratio(
        normalized_a,
        normalized_b,
    )

    return {
        "fuzzy_score": fuzzy_score,

        "same_category": int(
            features_a["category"]
            == features_b["category"]
        ),

        "room_class_both_known": int(
            is_known(features_a["room_class"])
            and is_known(features_b["room_class"])
        ),

        "same_room_class": int(
            is_known(features_a["room_class"])
            and is_known(features_b["room_class"])
            and features_a["room_class"]
            == features_b["room_class"]
        ),

        "view_both_known": int(
            is_known(features_a["view"])
            and is_known(features_b["view"])
        ),

        "same_view": int(
            is_known(features_a["view"])
            and is_known(features_b["view"])
            and features_a["view"]
            == features_b["view"]
        ),

        "bed_type_both_known": int(
            is_known(features_a["bed_type"])
            and is_known(features_b["bed_type"])
        ),

        "same_bed_type": int(
            is_known(features_a["bed_type"])
            and is_known(features_b["bed_type"])
            and features_a["bed_type"]
            == features_b["bed_type"]
        ),
        "bed_config_both_present": int(
            has_bed_configuration(features_a["bed_configuration"])
            and has_bed_configuration(features_b["bed_configuration"])
        ),

        "same_bed_configuration": int(
            has_bed_configuration(features_a["bed_configuration"])
            and has_bed_configuration(features_b["bed_configuration"])
            and features_a["bed_configuration"]
            == features_b["bed_configuration"]
        ),

        "same_balcony": int(
            features_a["balcony"]
            == features_b["balcony"]
        ),
    }