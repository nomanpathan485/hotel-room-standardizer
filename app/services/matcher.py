from rapidfuzz import fuzz
from app.services.ml_matcher import predict_room_match
from app.services.feature_extractor import extract_features
from app.services.normalizer import normalize_room_name
FILLER_WORDS = {"room", "with", "and"}


def _get_comparison_name(normalized_name: str) -> str:
    return " ".join(
        word
        for word in normalized_name.split()
        if word not in FILLER_WORDS
    )

MATCH = "match"
CONFLICT = "conflict"
UNKNOWN = "unknown"
def compare_feature(value_a, value_b, unknown_values=None):
    if unknown_values is None:
        unknown_values = {None, "unknown", "not_applicable"}
    if value_a in unknown_values or value_b in unknown_values:
        return UNKNOWN
    if value_a == value_b:
        return MATCH
    return CONFLICT

def has_hard_conflict(features_a: dict, features_b: dict) -> bool:
     # Smoking status
    smoking_status_a = features_a.get(
        "smoking_status",
        "unspecified",
    )
    smoking_status_b = features_b.get(
        "smoking_status",
        "unspecified",
    )

    a_is_smoking = smoking_status_a == "smoking"
    b_is_smoking = smoking_status_b == "smoking"

    # An unspecified room is treated as non-smoking.
    if a_is_smoking != b_is_smoking:
        return True

    # 1. Major room category
    category_a = features_a.get("category")
    category_b = features_b.get("category")

    category_result = compare_feature(
        category_a,
        category_b,
    )

    if category_result == CONFLICT:
        return True

    # 2. Building block versus bungalow
    block_a = features_a.get("building_block")
    block_b = features_b.get("building_block")

    a_is_block_without_bungalow = (
        block_a is not None
        and category_a != "bungalow"
    )

    b_is_block_without_bungalow = (
        block_b is not None
        and category_b != "bungalow"
    )

    if (
        category_a == "bungalow"
        and b_is_block_without_bungalow
    ):
        return True

    if (
        category_b == "bungalow"
        and a_is_block_without_bungalow
    ):
        return True

    # Explicitly different blocks must not match.
    if (
        block_a is not None
        and block_b is not None
        and block_a != block_b
    ):
        return True

    # 3. Room class
    room_class_result = compare_feature(
        features_a.get("room_class"),
        features_b.get("room_class"),
    )

    if room_class_result == CONFLICT:
        return True
    
    # suite subtype 
    suite_type_result = compare_feature(
        features_a.get("suite_type"),
        features_b.get("suite_type"),
    )

    if suite_type_result == CONFLICT:
        return True
    # Physical layout
    layout_result = compare_feature(
        features_a.get("layout"),
        features_b.get("layout"),
        unknown_values={"unknown", None},
    )

    if layout_result == CONFLICT:
        return True
    
    #view

    view_result =compare_feature(
        features_a.get("view"),
        features_b.get("view"),
    )
    if view_result == CONFLICT:
        return True
    #explicit bedcount
    bedroom_result = compare_feature(
        features_a.get("bedroom_count"),
        features_b.get("bedroom_count"),
    )
    if bedroom_result == CONFLICT:
        return True
    
    # 6. Dormitory bed count
    dorm_bed_result = compare_feature(
        features_a.get("dormitory_bed_count"),
        features_b.get("dormitory_bed_count"),
        unknown_values={None},
    )

    if dorm_bed_result == CONFLICT:
        return True

    # 7. Dormitory type
    dorm_type_result = compare_feature(
        features_a.get("dormitory_type"),
        features_b.get("dormitory_type"),
    )

    if dorm_type_result == CONFLICT:
        return True

   
    bed_result = compare_bed_configuration(
        features_a.get("bed_configuration", []),
        features_b.get("bed_configuration", []),
    )

    if bed_result == BED_CONFLICT:
        return True

   

    
    
    return False

def get_bed_specificity(bed_configuration: list[dict]) -> int:
    if not bed_configuration:
        return 0

    return len(
        {
            bed.get("type")
            for bed in bed_configuration
            if bed.get("type")
        }
    )

BED_MATCH = "bed_match"
BED_CONFLICT = "bed_conflict"
BED_UNKNOWN = "bed_unknown"
BED_PARTIAL = "bed_partial"
BED_SPECIFICITY_GAP = "bed_specificity_gap"
BED_COUNT_MISMATCH = "bed_count_mismatch"



def compare_bed_configuration(
    config_a: list[dict],
    config_b: list[dict],
) -> str:
    if not config_a and not config_b:
        return BED_UNKNOWN

    if not config_a or not config_b:
        detailed = config_a or config_b

        bed_types = {
            bed.get("type")
            for bed in detailed
            if bed.get("type")
        }

        if len(bed_types) <= 1:
            return BED_UNKNOWN

        return BED_SPECIFICITY_GAP

    types_a = {
        bed.get("type")
        for bed in config_a
        if bed.get("type")
    }

    types_b = {
        bed.get("type")
        for bed in config_b
        if bed.get("type")
    }

    if types_a.isdisjoint(types_b):
        return BED_CONFLICT

    if types_a != types_b:
        return BED_PARTIAL

    counts_a = {
        bed.get("type"): bed.get("count")
        for bed in config_a
        if bed.get("type")
    }

    counts_b = {
        bed.get("type"): bed.get("count")
        for bed in config_b
        if bed.get("type")
    }

    for bed_type in types_a:
        count_a = counts_a.get(bed_type)
        count_b = counts_b.get(bed_type)

        if (
            count_a is not None
            and count_b is not None
            and count_a != count_b
        ):
            return BED_COUNT_MISMATCH

    return BED_MATCH

def calculate_feature_score(features_a: dict,features_b: dict)-> int:
    score = 0
    # Same major category is useful evidence.
    if features_a.get("category") == features_b.get("category"):
        score += 15
    #same room class
    if (
        features_a.get("room_class") != "unknown"
        and features_a.get("room_class") == features_b.get("room_class")
    ):
        score += 20

    #same explicit view is strong evidence
    if(
        features_a.get("view") != "unknown"
        and features_a.get("view") == features_b.get("view")
    ):
        score +=25
        # suite
    if (
        features_a.get("suite_type") not in {"unknown", "not_applicable"}
        and features_a.get("suite_type") == features_b.get("suite_type")
    ):
        score += 25
          # Same explicit bedroom count is strong evidence.
    if (
        features_a.get("bedroom_count") is not None
        and features_a.get("bedroom_count") == features_b.get("bedroom_count")
    ):
        score += 20

    # Compare explicit bed configurations.
    bed_result = compare_bed_configuration(
    features_a.get("bed_configuration", []),
    features_b.get("bed_configuration", []),
    )

    if bed_result == BED_MATCH:
        score += 15

    elif bed_result == BED_PARTIAL:
        score -= 10

    elif bed_result == BED_SPECIFICITY_GAP:
        score -= 15

    elif bed_result == BED_COUNT_MISMATCH:
        score -= 20

    elif bed_result == BED_CONFLICT:
        score -= 30
    #balcony
    if features_a.get("balcony") != features_b.get("balcony"):
        score -= 10

    #club access diffrence
    if features_a.get("club_access") != features_b.get("club_access"):
        score -=15

    return score

def calculate_name_score(
    normalized_a: str,
    normalized_b: str,
) -> float:
    return fuzz.token_set_ratio(
        normalized_a,
        normalized_b,
    )

def calculate_final_score(
    room_a: dict,
    room_b: dict,
) -> float:
    features_a = room_a["features"]
    features_b = room_b["features"]

    if has_hard_conflict(features_a, features_b):
        return 0.0

    feature_score = calculate_feature_score(
        features_a,
        features_b,
    )

    name_score = calculate_name_score(
        room_a["normalized_name"],
        room_b["normalized_name"],
    )

    final_score = (
        name_score * 0.6
        + feature_score * 0.4
    )

    return final_score



def _same_view(view_a: str, view_b: str) -> bool:
    # "(No View)" / "No View" is supplier noise; treat it as transparent
    # so a "Garden View (No View)" room can still match a plain "Garden
    # View" room.
    if view_a == "no_view" or view_b == "no_view":
        return True
    return view_a == view_b


def _same_bed_configuration(
    config_a: list[dict],
    config_b: list[dict],
) -> bool:
    if not config_a and not config_b:
        return True

    if not config_a or not config_b:
        detailed_config = config_a or config_b

        detailed_types = {
            bed.get("type")
            for bed in detailed_config
            if bed.get("type")
        }

        if len(detailed_types) > 1:
            return False

        has_explicit_multiple_beds = any(
            bed.get("count") is not None
            and bed["count"] > 1
            for bed in detailed_config
        )

        if has_explicit_multiple_beds:
            return False
        if detailed_types == {"twin"}:
            return False

        # Missing bed information may match one simple bed,
        # but not multiple beds or multiple bed types.
        return True

    signature_a = {
        (
            bed.get("type"),
            1 if bed.get("count") is None else bed["count"],
        )
        for bed in config_a
        if bed.get("type")
    }

    signature_b = {
        (
            bed.get("type"),
            1 if bed.get("count") is None else bed["count"],
        )
        for bed in config_b
        if bed.get("type")
    }

    return signature_a == signature_b

def get_bed_signature(features: dict) -> set[tuple[str, int | None]]:
    return {
        (bed["type"], 1 if bed.get("count") is None else bed["count"])
        for bed in features.get("bed_configuration", [])
    }

def _compatible_standard_view_room(
    features_a: dict,
    features_b: dict,
) -> bool:
    same_view = features_a["view"] == features_b["view"]

    allowed_classes = {"standard", "unknown"}
    class_compatible = (
        features_a["room_class"] in allowed_classes
        and features_b["room_class"] in allowed_classes
    )

    allowed_beds = {"double", "unknown"}
    bed_compatible = (
        features_a["bed_type"] in allowed_beds
        and features_b["bed_type"] in allowed_beds
    )

    return same_view and class_compatible and bed_compatible



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
    if not _same_bed_configuration(
        bed_configuration_a,
        bed_configuration_b
    ):
        return False
        
# Bed signature mismatch
    if bed_signature_a and bed_signature_b:
        if bed_signature_a != bed_signature_b:
            return False

    # Final fuzzy comparison
    score = fuzz.token_set_ratio(normalized_a, normalized_b)

    return score >= threshold

def is_match_v2(
    room_a: dict,
    room_b: dict,
    threshold: float = 70.0,
) -> bool:
    final_score = calculate_final_score(
        room_a,
        room_b,
    )

    return final_score >= threshold

def diagnose_match(
    room_a: dict,
    room_b: dict,
    threshold: int = 90,
) -> dict:
    normalized_a = room_a["normalized_name"]
    normalized_b = room_b["normalized_name"]

    if normalized_a == normalized_b:
        return {
            "matched": True,
            "reason": "exact_name",
            "score": 100,
        }

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

    bed_configuration_a = features_a.get(
        "bed_configuration",
        [],
    )

    bed_configuration_b = features_b.get(
        "bed_configuration",
        [],
    )

    # Category
    if category_a != category_b:
        return {
            "matched": False,
            "reason": "category",
            "value_a": category_a,
            "value_b": category_b,
        }

    # Room class
    if room_class_a != room_class_b:
        return {
            "matched": False,
            "reason": "room_class",
            "value_a": room_class_a,
            "value_b": room_class_b,
        }

    # Suite type
    if suite_type_a != suite_type_b:
        return {
            "matched": False,
            "reason": "suite_type",
            "value_a": suite_type_a,
            "value_b": suite_type_b,
        }

    # Bedroom count
    if bedroom_count_a != bedroom_count_b:
        return {
            "matched": False,
            "reason": "bedroom_count",
            "value_a": bedroom_count_a,
            "value_b": bedroom_count_b,
        }

    # Club access
    if club_access_a != club_access_b:
        return {
            "matched": False,
            "reason": "club_access",
            "value_a": club_access_a,
            "value_b": club_access_b,
        }

    # Dormitory rules
    if category_a == "dormitory":
        if bed_count_a is None or bed_count_b is None:
            return {
                "matched": False,
                "reason": "dormitory_bed_count_missing",
            }

        if bed_count_a != bed_count_b:
            return {
                "matched": False,
                "reason": "dormitory_bed_count",
                "value_a": bed_count_a,
                "value_b": bed_count_b,
            }

        if (
            dormitory_type_a != "unknown"
            and dormitory_type_b != "unknown"
            and dormitory_type_a != dormitory_type_b
        ):
            return {
                "matched": False,
                "reason": "dormitory_type",
                "value_a": dormitory_type_a,
                "value_b": dormitory_type_b,
            }

        return {
            "matched": True,
            "reason": "dormitory_match",
            "score": 100,
        }

    # View
    if not _same_view(view_a, view_b):
        return {
            "matched": False,
            "reason": "view",
            "value_a": view_a,
            "value_b": view_b,
        }

    # Balcony
    if balcony_a != balcony_b:
        return {
            "matched": False,
            "reason": "balcony",
            "value_a": balcony_a,
            "value_b": balcony_b,
        }

    # Terrace
    if terrace_a != terrace_b:
        return {
            "matched": False,
            "reason": "terrace",
            "value_a": terrace_a,
            "value_b": terrace_b,
        }

    # Bed type
    bed_type_a = features_a["bed_type"]
    bed_type_b = features_b["bed_type"]

    if bed_type_a != bed_type_b:
        return {
            "matched": False,
            "reason": "bed_type",
            "value_a": bed_type_a,
            "value_b": bed_type_b,
        }

    # Bed configuration
    if not _same_bed_configuration(
        bed_configuration_a,
        bed_configuration_b,
    ):
        return {
            "matched": False,
            "reason": "bed_configuration",
            "value_a": bed_configuration_a,
            "value_b": bed_configuration_b,
        }

    # Bed signature
    if bed_signature_a and bed_signature_b:
        if bed_signature_a != bed_signature_b:
            return {
                "matched": False,
                "reason": "bed_signature",
                "value_a": list(bed_signature_a),
                "value_b": list(bed_signature_b),
            }

    # Fuzzy
    score = fuzz.token_set_ratio(
        normalized_a,
        normalized_b,
    )

    return {
        "matched": score >= threshold,
        "reason": (
            "fuzzy_pass"
            if score >= threshold
            else "fuzzy_score"
        ),
        "score": score,
    }

def is_match_v3(room_a, room_b, threshold=90):
    normalized_a = room_a["normalized_name"]
    normalized_b = room_b["normalized_name"]

    # Exact match
    if normalized_a == normalized_b:
        return True

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

    bed_configuration_a = features_a.get(
        "bed_configuration",
        [],
    )
    bed_configuration_b = features_b.get(
        "bed_configuration",
        [],
    )

    # Different room categories
    if category_a != category_b:
        return False

    # V3 EXPERIMENT:
    # Reject only when BOTH room classes are known
    # and explicitly different.
    if (
        room_class_a != "unknown"
        and room_class_b != "unknown"
        and room_class_a != room_class_b
    ):
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

    # Different views
    if not _same_view(view_a, view_b):
        return False

    # Balcony mismatch
    if balcony_a != balcony_b:
        return False

    # Terrace mismatch
    if terrace_a != terrace_b:
        return False

    bed_type_a = features_a["bed_type"]
    bed_type_b = features_b["bed_type"]

    if bed_type_a != bed_type_b:
        return False

    # Bed configuration
    if not _same_bed_configuration(
        bed_configuration_a,
        bed_configuration_b,
    ):
        return False

    # Bed signature mismatch
    if bed_signature_a and bed_signature_b:
        if bed_signature_a != bed_signature_b:
            return False

    # Final fuzzy comparison
    score = fuzz.token_set_ratio(
        normalized_a,
        normalized_b,
    )

    return score >= threshold

def has_explicit_sofa_bed(
    bed_configuration: list[dict],
) -> bool:
    return any(
        bed.get("type") == "sofa"
        for bed in bed_configuration
    )



def is_match_v4(room_a, room_b, threshold=90):
    normalized_a = room_a["normalized_name"]
    normalized_b = room_b["normalized_name"]

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
    layout_a = features_a.get("layout", "unknown")
    layout_b = features_b.get("layout", "unknown")

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

    swim_up_a = features_a.get("swim_up", False)
    swim_up_b = features_b.get("swim_up", False)

    annex_a = features_a.get("annex", False)
    annex_b = features_b.get("annex", False)

    jacuzzi_a = features_a.get("jacuzzi", False)
    jacuzzi_b = features_b.get("jacuzzi", False)

    bed_relation_a = features_a.get("bed_relation", "unknown")
    bed_relation_b = features_b.get("bed_relation", "unknown")

    bed_count_a = features_a["dormitory_bed_count"]
    bed_count_b = features_b["dormitory_bed_count"]

    dormitory_type_a = features_a["dormitory_type"]
    dormitory_type_b = features_b["dormitory_type"]

    bed_configuration_a = features_a.get(
        "bed_configuration",
        [],
    )

    bed_configuration_b = features_b.get(
        "bed_configuration",
        [],
    )

    # Different explicit accommodation categories are a hard conflict.
    # "unknown" means the supplier did not mention the category.
    if (
        category_a != "unknown"
        and category_b != "unknown"
        and category_a != category_b
    ):
        return False

    # V3 change:
    # unknown room class is treated as missing information
    if (
        room_class_a != "unknown"
        and room_class_b != "unknown"
        and room_class_a != room_class_b
    ):
        return False

    # Different explicit suite subtypes are a hard conflict.
    # "unknown" means the supplier did not provide the subtype.
    if (
        category_a == "suite"
        and suite_type_a not in {"unknown", "not_applicable"}
        and suite_type_b not in {"unknown", "not_applicable"}
        and suite_type_a != suite_type_b
    ):
        return False
    # Different explicit layouts are a hard conflict.
    # "unknown" means the supplier did not mention the layout.
    if (
        layout_a != "unknown"
        and layout_b != "unknown"
        and layout_a != layout_b
    ):
        return False

    if bedroom_count_a != bedroom_count_b:
        return False

    if club_access_a != club_access_b:
        return False

    # Dormitory rules
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

    # View stays strict
    if not _same_view(view_a, view_b):
        return False

    # Balcony stays strict for this experiment
    if balcony_a != balcony_b:
        return False

    # Terrace stays strict
    if terrace_a != terrace_b:
        return False
    
    if swim_up_a != swim_up_b:
        return False
    if annex_a != annex_b:
        return False
    if jacuzzi_a != jacuzzi_b:
        return False
    if (
        bed_relation_a != "unknown"
        and bed_relation_b != "unknown"
        and bed_relation_a != bed_relation_b
    ):
        return False
    # Exact normalized names can match only after
    # all semantic contradictions have been checked.
    if normalized_a == normalized_b:
        return True
    
    bed_type_a = features_a["bed_type"]
    bed_type_b = features_b["bed_type"]

    # V4 change:
    # unknown bed type is treated as missing information
    
    if category_a == "suite":
        sofa_a = has_explicit_sofa_bed(
            bed_configuration_a
        )
        sofa_b = has_explicit_sofa_bed(
            bed_configuration_b
        )

        if sofa_a != sofa_b:
            return False
    if (
        bed_type_a != "unknown"
        and bed_type_b != "unknown"
        and bed_type_a != bed_type_b
    ):
        return False
    

    # Bed configuration stays exactly like V1
    if not _same_bed_configuration(
        bed_configuration_a,
        bed_configuration_b,
    ):
        return False

    # Bed signature stays strict
    if bed_signature_a and bed_signature_b:
        if bed_signature_a != bed_signature_b:
            return False

    name_a = room_a["normalized_name"]
    name_b = room_b["normalized_name"]

    score = fuzz.token_set_ratio(
        name_a,
        name_b,
    )
    
    # Narrow suite rule:
    # Same explicit suite subtype can tolerate lower similarity.
    if (
        category_a == "suite"
        and category_b == "suite"
        and suite_type_a == suite_type_b
        and suite_type_a not in {
            "unknown",
            "standard",
            "not_applicable",
        }
    ):
        return score >= 70

    if (
        category_a == "room"
        and category_b == "room"
        and view_a == view_b
        and view_a != "unknown"
        and {
            room_class_a,
            room_class_b,
        }.issubset({"standard", "unknown"})
    ):
        return score >= 89

    # Default rule must remain last.
    return score >= threshold

def diagnose_match_v4(
    room_a: dict,
    room_b: dict,
    threshold: int = 90,
) -> dict:
    normalized_a = room_a["normalized_name"]
    normalized_b = room_b["normalized_name"]

    if normalized_a == normalized_b:
        return {
            "matched": True,
            "reason": "exact_name",
            "score": 100,
        }

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

    if category_a != category_b:
        return {
            "matched": False,
            "reason": "category",
        }

    if (
        room_class_a != "unknown"
        and room_class_b != "unknown"
        and room_class_a != room_class_b
    ):
        return {
            "matched": False,
            "reason": "room_class",
        }

    if suite_type_a != suite_type_b:
        return {
            "matched": False,
            "reason": "suite_type",
        }

    if bedroom_count_a != bedroom_count_b:
        return {
            "matched": False,
            "reason": "bedroom_count",
        }

    if club_access_a != club_access_b:
        return {
            "matched": False,
            "reason": "club_access",
        }

    if category_a == "dormitory":
        if bed_count_a is None or bed_count_b is None:
            return {
                "matched": False,
                "reason": "dormitory_bed_count_missing",
            }

        if bed_count_a != bed_count_b:
            return {
                "matched": False,
                "reason": "dormitory_bed_count",
            }

        if (
            dormitory_type_a != "unknown"
            and dormitory_type_b != "unknown"
            and dormitory_type_a != dormitory_type_b
        ):
            return {
                "matched": False,
                "reason": "dormitory_type",
            }

        return {
            "matched": True,
            "reason": "dormitory_match",
            "score": 100,
        }

    if not _same_view(view_a, view_b):
        return {
            "matched": False,
            "reason": "view",
        }

    if balcony_a != balcony_b:
        return {
            "matched": False,
            "reason": "balcony",
        }

    if terrace_a != terrace_b:
        return {
            "matched": False,
            "reason": "terrace",
        }

    bed_type_a = features_a["bed_type"]
    bed_type_b = features_b["bed_type"]

    if (
        bed_type_a != "unknown"
        and bed_type_b != "unknown"
        and bed_type_a != bed_type_b
    ):
        return {
            "matched": False,
            "reason": "bed_type",
        }

    if not _same_bed_configuration(
        bed_configuration_a,
        bed_configuration_b,
    ):
        return {
            "matched": False,
            "reason": "bed_configuration",
        }

    if bed_signature_a and bed_signature_b:
        if bed_signature_a != bed_signature_b:
            return {
                "matched": False,
                "reason": "bed_signature",
            }

    score = fuzz.token_set_ratio(
        normalized_a,
        normalized_b,
    )

    # Same explicit suite subtype can tolerate lower fuzzy similarity.
    if (
        category_a == "suite"
        and category_b == "suite"
        and suite_type_a == suite_type_b
        and suite_type_a not in {
            "unknown",
            "standard",
            "not_applicable",
        }
    ):
        matched = score >= 70

    # Standard/unknown room class with the same explicit view
    # can tolerate a very small fuzzy drop.
    elif (
        category_a == "room"
        and category_b == "room"
        and view_a == view_b
        and view_a != "unknown"
        and {
            room_class_a,
            room_class_b,
        }.issubset(
            {
                "standard",
                "unknown",
            }
        )
    ):
        matched = score >= 89

    else:
        matched = score >= threshold


    return {
        "matched": matched,
        "reason": (
            "fuzzy_pass"
            if matched
            else "fuzzy_score"
        ),
        "score": score,
    }
def _passes_ml_model(
    room_a: dict,
    room_b: dict,
    probability_threshold: float = 0.85,
) -> bool:
    normalized_a = _get_normalized_name(room_a)
    normalized_b = _get_normalized_name(room_b)

    features_a = _get_features(room_a)
    features_b = _get_features(room_b)

    if has_hard_conflict(features_a, features_b):
        return False

    if normalized_a == normalized_b:
        return True

    prediction = predict_room_match(
        room_a_name=normalized_a,
        room_b_name=normalized_b,
    )

    print("\nML PREDICTION:")
    print(prediction)

    return (
        prediction["match_probability"]
        >= probability_threshold
    )
from enum import Enum

from rapidfuzz.fuzz import token_set_ratio


class MatchDecision(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    UNCERTAIN = "UNCERTAIN"


UNKNOWN_VALUES = {
    None,
    "",
    "unknown",
    "not_applicable",
}


def _get_features(room: dict) -> dict:
    return room.get("features") or extract_features(
        room["room_name"]
    )


def _get_normalized_name(room: dict) -> str:
    return room.get("normalized_name") or normalize_room_name(
        room["room_name"]
    )


def collect_positive_evidence(
    features_a: dict,
    features_b: dict,
) -> list[str]:
    evidence = []

    important_features = [
        "building_block",
        "category",
        "room_class",
        "suite_type",
        "layout",
        "view",
        "bed_type",
        "bedroom_count",
        "occupancy",
        "bed_relation",
    ]

    for feature_name in important_features:
        value_a = features_a.get(feature_name)
        value_b = features_b.get(feature_name)

        if value_a in UNKNOWN_VALUES or value_b in UNKNOWN_VALUES:
            continue

        # Generic "room" is too weak to prove identity.
        if feature_name == "category" and value_a == "room":
            continue

        if value_a == value_b:
            evidence.append(feature_name)

    bed_config_a = features_a.get("bed_configuration") or []
    bed_config_b = features_b.get("bed_configuration") or []

    if bed_config_a and bed_config_b:
        if bed_config_a == bed_config_b:
            evidence.append("bed_configuration")

    return evidence

def collect_identity_asymmetries(
    features_a: dict,
    features_b: dict,
) -> list[str]:
    asymmetries = []

    categorical_features = {
        "room_class": "unknown",
        "view": "unknown",
        "layout": "unknown",
        "building_block": None,
        "bedroom_count": None,
    }

    for feature_name, unknown_value in categorical_features.items():
        value_a = features_a.get(feature_name, unknown_value)
        value_b = features_b.get(feature_name, unknown_value)

        a_is_known = value_a != unknown_value
        b_is_known = value_b != unknown_value

        if a_is_known != b_is_known:
            asymmetries.append(feature_name)

    # Compare category only once.
    category_a = features_a.get("category", "unknown")
    category_b = features_b.get("category", "unknown")

    generic_categories = {
        "unknown",
        "room",
    }

    a_is_distinctive = category_a not in generic_categories
    b_is_distinctive = category_b not in generic_categories

    if a_is_distinctive != b_is_distinctive:
        asymmetries.append("category")

    distinctive_flags = [
        "luxury_variant",
        "overwater",
        "club_access",
        "connecting_room",
        "swim_up",
        "pool_access",
        "annex",
        "jacuzzi",
        "hot_tub",
    ]

    for feature_name in distinctive_flags:
        value_a = bool(features_a.get(feature_name, False))
        value_b = bool(features_b.get(feature_name, False))

        if value_a != value_b:
            asymmetries.append(feature_name)

    # Swim-up already implies pool access, so these count
    # as one asymmetry rather than two.
    if (
        "swim_up" in asymmetries
        and "pool_access" in asymmetries
    ):
        asymmetries.remove("pool_access")

    identity_tokens_a = set(
        features_a.get("identity_tokens") or []
    )
    identity_tokens_b = set(
        features_b.get("identity_tokens") or []
    )

    if identity_tokens_a != identity_tokens_b:
        asymmetries.append("identity_tokens")

    return asymmetries
GENERIC_ROOM_WORDS = {
    "room",
    "rooms",
    "guest",
    "guestroom",
}

RECOGNIZED_ROOM_CLASSES = {
    "standard",
    "superior",
    "deluxe",
    "premium",
    "premier",
    "executive",
    "club",
    "classic",
    "comfort",
    "business",
    "luxury",
}


def is_class_only_equivalent(
    normalized_a: str,
    normalized_b: str,
) -> bool:
    tokens_a = normalized_a.split()
    tokens_b = normalized_b.split()

    core_tokens_a = [
        token
        for token in tokens_a
        if token not in GENERIC_ROOM_WORDS
    ]

    core_tokens_b = [
        token
        for token in tokens_b
        if token not in GENERIC_ROOM_WORDS
    ]

    return (
        core_tokens_a == core_tokens_b
        and len(core_tokens_a) == 1
        and core_tokens_a[0] in RECOGNIZED_ROOM_CLASSES
    )


def decide_room_match_ml(
    room_a: dict,
    room_b: dict,
    probability_threshold: float = 0.85,
) -> MatchDecision:
    features_a = _get_features(room_a)
    features_b = _get_features(room_b)
    
    if has_hard_conflict(features_a, features_b):
        return MatchDecision.NO_MATCH

    normalized_a = _get_normalized_name(room_a)
    normalized_b = _get_normalized_name(room_b)

    token_set_score = fuzz.token_set_ratio(
        normalized_a,
        normalized_b,
    )

    token_sort_score = fuzz.token_sort_ratio(
        normalized_a,
        normalized_b,
    )

    positive_evidence = collect_positive_evidence(
        features_a,
        features_b,
    )

    exact_name_match = (
        bool(normalized_a)
        and normalized_a == normalized_b
    )

    if exact_name_match:
        return MatchDecision.MATCH
    if is_class_only_equivalent(
        normalized_a,
        normalized_b,
    ):
        return MatchDecision.MATCH

    identity_asymmetries = collect_identity_asymmetries(
        features_a,
        features_b,
    )
    bedroom_count_a = features_a.get("bedroom_count")
    bedroom_count_b = features_b.get("bedroom_count")

    identity_tokens_a = set(
        features_a.get("identity_tokens") or []
    )
    identity_tokens_b = set(
        features_b.get("identity_tokens") or []
    )

    shared_identity_tokens = (
        identity_tokens_a & identity_tokens_b
    )

    # Do not count the shared view twice as identity evidence.
    shared_non_view_tokens = shared_identity_tokens - {
        features_a.get("view"),
        features_b.get("view"),
    }
    if shared_non_view_tokens:
        positive_evidence.append("identity_tokens")

    safe_single_bedroom_omission = (
        "bedroom_count" in identity_asymmetries
        and {bedroom_count_a, bedroom_count_b} == {None, 1}
        and features_a.get("category") == "suite"
        and features_b.get("category") == "suite"
        and features_a.get("view") == features_b.get("view")
        and features_a.get("view") not in {"unknown", None}
        and features_a.get("bed_type") == features_b.get("bed_type")
        and features_a.get("bed_type") not in {"unknown", None}
        and bool(shared_non_view_tokens)
    )

    if safe_single_bedroom_omission:
        identity_asymmetries.remove("bedroom_count")

    automatic_match_allowed = not identity_asymmetries

    strong_name_evidence = (
        token_sort_score >= 90
        and len(positive_evidence) >= 1
        and automatic_match_allowed
    )

    strong_semantic_evidence = (
        token_set_score >= 85
        and len(positive_evidence) >= 2
        and automatic_match_allowed
    )
    strong_identity_evidence = (
        token_set_score == 100
        and bool(shared_non_view_tokens)
        and automatic_match_allowed
    )
    print("\nMATCH DIAGNOSTICS")
    print("NORMALIZED A:", normalized_a)
    print("NORMALIZED B:", normalized_b)
    print("TOKEN SET SCORE:", token_set_score)
    print("TOKEN SORT SCORE:", token_sort_score)
    print("POSITIVE EVIDENCE:", positive_evidence)
    print("IDENTITY ASYMMETRIES:", identity_asymmetries)
    print("STRONG NAME:", strong_name_evidence)
    print("STRONG SEMANTIC:", strong_semantic_evidence)
    print("STRONG IDENTITY:", strong_identity_evidence)
    print("AUTOMATIC MATCH ALLOWED:", automatic_match_allowed)
        

    if not (
        strong_name_evidence
        or strong_semantic_evidence
        or strong_identity_evidence
    ):
        
        return MatchDecision.UNCERTAIN

    model_accepts_pair = _passes_ml_model(
        room_a,
        room_b,
        probability_threshold=probability_threshold,
    )

    if model_accepts_pair:
        return MatchDecision.MATCH

    return MatchDecision.NO_MATCH

def is_match_ml(
    room_a: dict,
    room_b: dict,
    probability_threshold: float = 0.85,
) -> bool:
    decision = decide_room_match_ml(
        room_a,
        room_b,
        probability_threshold=probability_threshold,
    )

    return decision == MatchDecision.MATCH