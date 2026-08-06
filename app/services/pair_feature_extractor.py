from rapidfuzz.fuzz import (
    ratio,
    token_set_ratio,
    token_sort_ratio,
)
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

def bed_types_are_compatible(
    bed_type_a: str,
    bed_type_b: str,
) -> bool:
    if not (
        is_known(bed_type_a)
        and is_known(bed_type_b)
    ):
        return False

    compatible_beds = {
        "double_or_twin": {"double", "twin"},
        "double": {"double"},
        "twin": {"twin"},
        "king": {"king"},
        "queen": {"queen"},
        "bunk": {"bunk"},
        "sofa": {"sofa"},
    }

    beds_a = compatible_beds.get(
        bed_type_a,
        {bed_type_a},
    )
    beds_b = compatible_beds.get(
        bed_type_b,
        {bed_type_b},
    )

    return bool(beds_a & beds_b)

def extract_pair_features(
    room_a_name: str,
    room_b_name: str,
) -> dict:
    normalized_a = normalize_room_name(room_a_name)
    normalized_b = normalize_room_name(room_b_name)

    tokens_a = normalized_a.split()
    tokens_b = normalized_b.split()

    ordinary_ratio = ratio(
        normalized_a,
        normalized_b,
    )

    sorted_token_ratio = token_sort_ratio(
        normalized_a,
        normalized_b,
    )

    character_length_ratio = (
        min(len(normalized_a), len(normalized_b))
        / max(len(normalized_a), len(normalized_b))
        if normalized_a and normalized_b
        else 0
    )

    token_count_ratio = (
        min(len(tokens_a), len(tokens_b))
        / max(len(tokens_a), len(tokens_b))
        if tokens_a and tokens_b
        else 0
    )

    features_a = extract_features(room_a_name)
    features_b = extract_features(room_b_name)

    identity_tokens_a = set(
        features_a.get("identity_tokens") or []
    )
    identity_tokens_b = set(
        features_b.get("identity_tokens") or []
    )

    shared_identity_tokens = (
        identity_tokens_a & identity_tokens_b
    )

    identity_tokens_both_present = (
        bool(identity_tokens_a)
        and bool(identity_tokens_b)
    )

    shared_identity_token = bool(
        shared_identity_tokens
    )

    identity_token_overlap_ratio = (
        len(shared_identity_tokens)
        / min(
            len(identity_tokens_a),
            len(identity_tokens_b),
        )
        if identity_tokens_both_present
        else 0.0
    )
    luxury_variant_mismatch = (
        features_a["luxury_variant"]
        != features_b["luxury_variant"]
    )

    overwater_mismatch = (
        features_a["overwater"]
        != features_b["overwater"]
    )
    bedroom_count_a = features_a["bedroom_count"]
    bedroom_count_b = features_b["bedroom_count"]

    bedroom_count_both_known = (
        bedroom_count_a is not None
        and bedroom_count_b is not None
    )

    same_bedroom_count = (
        bedroom_count_both_known
        and bedroom_count_a == bedroom_count_b
    )
    bed_type_a = features_a["bed_type"]
    bed_type_b = features_b["bed_type"]
    bed_type_both_known = (
        is_known(bed_type_a)
        and is_known(bed_type_b)
    )

    bed_assignment_uncertain = (
        features_a["bed_assignment_uncertain"]
        or features_b["bed_assignment_uncertain"]
    )

    bed_type_compatible = (
        (
            bed_type_both_known
            and bed_types_are_compatible(
                bed_type_a,
                bed_type_b,
            )
        )
        or bed_assignment_uncertain
    )
    fuzzy_score = token_set_ratio(
        normalized_a,
        normalized_b,
    )

    occupancy_both_known = (
        features_a["occupancy"] is not None
        and features_b["occupancy"] is not None
    )

    same_occupancy = (
        occupancy_both_known
        and features_a["occupancy"]
        == features_b["occupancy"]
    )

    return {
        "fuzzy_score": fuzzy_score,
        "ordinary_ratio": ordinary_ratio,
        "token_sort_ratio": sorted_token_ratio,
        "character_length_ratio": character_length_ratio,
        "token_count_ratio": token_count_ratio,

        "same_category": int(
            features_a["category"]
            == features_b["category"]
        ),
        "identity_tokens_both_present": int(
            identity_tokens_both_present
        ),

        "shared_identity_token": int(
            shared_identity_token
        ),

        "identity_token_overlap_ratio": (
            identity_token_overlap_ratio
        ),

        "identity_token_mismatch": int(
            identity_tokens_both_present
            and not shared_identity_token
        ),
        "luxury_variant_mismatch": int(
            luxury_variant_mismatch
        ),

        "overwater_mismatch": int(
            overwater_mismatch
        ),
        "bedroom_count_both_known": int(
            bedroom_count_both_known
        ),

        "same_bedroom_count": int(
            same_bedroom_count
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
            bed_type_both_known
        ),

        "same_bed_type": int(
            bed_type_both_known
            and bed_type_a == bed_type_b
        ),
        "bed_type_compatible": int(
            bed_type_compatible
        ),

        "bed_config_both_present": int(
            has_bed_configuration(
                features_a["bed_configuration"]
            )
            and has_bed_configuration(
                features_b["bed_configuration"]
            )
        ),

        "same_bed_configuration": int(
            has_bed_configuration(
                features_a["bed_configuration"]
            )
            and has_bed_configuration(
                features_b["bed_configuration"]
            )
            and features_a["bed_configuration"]
            == features_b["bed_configuration"]
        ),

        "occupancy_both_known": int(
            occupancy_both_known
        ),

        "same_occupancy": int(
            same_occupancy
        ),
        "both_single_use": int(
            features_a["single_use"]
            and features_b["single_use"]
        ),
        "single_use_mismatch": int(
            features_a["single_use"]
            != features_b["single_use"]
        ),
        "both_balcony": int(
            features_a["balcony"]
            and features_b["balcony"]
        ),
        "balcony_mismatch": int(
            features_a["balcony"]
            != features_b["balcony"]
        ),
        "both_pool_access": int(
            features_a["pool_access"]
            and features_b["pool_access"]
        ),

        "pool_access_mismatch": int(
            features_a["pool_access"]
            != features_b["pool_access"]
        ),

        "both_swim_up": int(
            features_a["swim_up"]
            and features_b["swim_up"]
        ),

        "swim_up_mismatch": int(
            features_a["swim_up"]
            != features_b["swim_up"]
        ),
    }