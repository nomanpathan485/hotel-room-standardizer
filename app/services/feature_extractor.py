import re

from app.services.normalizer import normalize_room_name

def get_identity_tokens(room_name: str) -> list[str]:
    """
    Return words that are not already explained by known room features.

    Examples:
    Apollo Room Sea View King Bed -> ["apollo"]
    King Bed Sea View             -> []
    Deluxe King Room              -> []
    Emerald Room Ocean View       -> ["emerald"]
    """
    normalized_name = normalize_room_name(room_name)

    generic_tokens = {
        # Generic room words
        "room",
        "rooms",
        "guest",
        "guestroom",
        "accommodation",
        "unit",
        "views",
        "size",
        "grande",

        # Categories
        "dormitory",
        "dorm",
        "suite",
        "studio",
        "apartment",
        "apartments",
        "apt",
        "villa",
        "bungalow",
        "chalet",
        "cabin",
        "cabana",
        "capsule",
        "pod",
        "cottage",
        "tent",
        "penthouse",

        # Room classes and suite types
        "standard",
        "presidential",
        "diplomatic",
        "royal",
        "signature",
        "prestige",
        "luxury",
        "grand",
        "panoramic",
        "premium",
        "premier",
        "executive",
        "club",
        "deluxe",
        "superior",
        "comfort",
        "classic",
        "business",
        "junior",
        "senior",
        "family",
        "honeymoon",
        "bridal",
        "ambassador",
        "emirates",

        # Bed vocabulary
        "bed",
        "beds",
        "bedroom",
        "bedrooms",
        "king",
        "queen",
        "twin",
        "double",
        "single",
        "full",
        "bunk",
        "sofa",

        # View vocabulary
        "view",
        "seaview",
        "sea",
        "ocean",
        "garden",
        "city",
        "pool",
        "marina",
        "beach",
        "beachfront",
        "lagoon",
        "river",
        "mountain",
        "mountainside",
        "land",
        "desert",
        "skyline",
        "fountain",
        "burj",
        "khalifa",
        "eiger",
        "partial",
        "side",
        "lateral",
        "limited",
        "facing",

        # Layout and physical attributes
        "duplex",
        "dublex",
        "split",
        "level",
        "maisonette",
        "loft",
        "mezzanine",
        "balcony",
        "terrace",
        "connecting",
        "annex",
        "jacuzzi",
        "tub",
        "swim",
        "access",
        "overwater",

        # Occupancy and linking words
        "person",
        "persons",
        "adult",
        "adults",
        "guest",
        "guests",
        "pax",
        "use",
        "with",
        "without",
        "and",
        "or",
        "the",
        "of",
        "in",
        "on",
        "to",
        "for",

        # Number words
        "one",
        "two",
        "three",
        "four",
        "five",

        # Common supplier/rate noise
        "rate",
        "package",
        "breakfast",
        "non",
        "smoking",
        "available",
        "subject",
        "availability",
        "only",
    }

    tokens = re.findall(r"\b[a-z]+\b", normalized_name)

    return sorted({
        token
        for token in tokens
        if token not in generic_tokens
    })

SINGLE_USE_KEYWORDS = [
    "single use",
    "single occupancy",
    "sgl",
    "su",
]
def is_single_use(room_name: str):
    text = room_name.lower()

    for keyword in SINGLE_USE_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            return True

    return False

OCCUPANCY_KEYWORDS = {

    "single": 1,
    "double": 2,
    "twin": 2,
    "triple": 3,
    "quad": 4,
    "quadruple": 4,
}
def get_occupancy(room_name: str):
    text = room_name.lower()

    numeric_match = re.search(
        r"\b(\d+)\s*(person|persons|adult|adults|guest|guests|pax)\b",
        text,
    )

    if numeric_match:
        return int(numeric_match.group(1))

    occupancy_text = text

    for keyword in SINGLE_USE_KEYWORDS:
        occupancy_text = re.sub(
            rf"\b{re.escape(keyword)}\b",
            " ",
            occupancy_text,
        )

    # Check explicit room-capacity words before bed descriptions.
    capacity_patterns = [
        (r"\bquadruple\b", 4),
        (r"\bquad\b", 4),
        (r"\btriple\b", 3),
        (r"\bdouble\b", 2),
        (r"\btwin\b", 2),
        (r"\bsingle\b", 1),
    ]

    for pattern, occupancy in capacity_patterns:
        if re.search(pattern, occupancy_text):
            return occupancy

    return None

def get_room_category(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    category_patterns = [
        ("dormitory", r"\b(?:dormitory|dorm)\b"),
        ("suite", r"\bsuite\b"),
        ("studio", r"\bstudio\b"),
        ("apartment", r"\b(?:apartment|apartments|apt)\b"),
        ("villa", r"\bvilla\b"),
        ("bungalow", r"\bbungalow\b"),
        ("chalet", r"\bchalet\b"),
        ("cabin", r"\bcabin\b"),
        ("cabana", r"\bcabana\b"),
        ("capsule", r"\b(?:capsule|pod)\b"),
        ("cottage", r"\bcottage\b"),
        ("tent", r"\btent\b"),
        ("penthouse", r"\bpenthouse\b"),
        ("room", r"\broom\b"),
    ]

    for category, pattern in category_patterns:
        if re.search(pattern, room_name):
            return category

    return "unknown"

def get_room_class(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    # These are supplier phrases, not physical room classes.
    room_name = re.sub(
        r"\bstandard\s+(?:rate|bedroom)\b",
        " ",
        room_name,
    )

    # Order represents precedence when multiple class terms appear.
    # More distinctive classes must be checked before generic "standard".
    class_precedence = [
        "presidential",
        "diplomatic",
        "royal",
        "signature",
        "prestige",
        "luxury",
        "grand",
        "panoramic",
        "premium",
        "premier",
        "executive",
        "club",
        "deluxe",
        "superior",
        "comfort",
        "classic",
        "business",
        "standard",
    ]

    for room_class in class_precedence:
        if re.search(rf"\b{re.escape(room_class)}\b", room_name):
            return room_class

    return "unknown"

def get_suite_type(room_name: str) -> str:

    room_name = normalize_room_name(room_name)

    if not re.search(r"\bsuite\b", room_name):
        return "not_applicable"

    suite_type_patterns = {
        "presidential": r"\bpresidential\b",
        "royal": r"\broyal\b",
        "junior": r"\bjunior\b",
        "senior": r"\bsenior\b",
        "family": r"\bfamily\b",
        "executive": r"\bexecutive\b",
        "honeymoon": r"\bhoneymoon\b",
        "bridal": r"\bbridal\b",
        "penthouse": r"\bpenthouse\b",
        "prestige": r"\bprestige\b",
        "signature": r"\bsignature\b",
        "diplomatic": r"\bdiplomatic\b",
        "ambassador": r"\bambassador\b",
        "emirates": r"\bemirates\b",
    }

    for suite_type, pattern in suite_type_patterns.items():
        if re.search(pattern, room_name):
            return suite_type

    return "unknown"
def get_layout(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    layout_patterns = [
        ("duplex", r"\b(?:duplex|dublex)\b"),
        ("split_level", r"\b(?:split level|bi level)\b"),
        ("maisonette", r"\bmaisonette\b"),
        ("loft", r"\bloft\b"),
        ("mezzanine", r"\bmezzanine\b"),
    ]

    for layout, pattern in layout_patterns:
        if re.search(pattern, room_name):
            return layout

    return "unknown"

def get_bed_type(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    if re.search(
        r"\b(?:double\s+(?:or\s+)?twin|twin\s+(?:or\s+)?double)\b",
        room_name,
    ):
        return "double_or_twin"
    # Bed style takes priority over bed size.
    if re.search(r"\b(?:twin\s+)?bunk beds?\b", room_name):
        return "bunk"

    if (
        re.search(r"\bsofa beds?\b", room_name)
        and not re.search(
            r"\b(?:king|queen|double|twin|single)\s+bed\b",
            room_name,
        )
    ):
        return "sofa"
    # An explicit "double bed" is stronger than a standalone "twin".
    if (
        re.search(r"\b(?:full\s+)?double beds?\b", room_name)
        and not re.search(r"\btwin beds?\b", room_name)
        and not re.search(r"\b(?:king|queen) beds?\b", room_name)
    ):
        return "double"

    bed_patterns = {
        "king": [
            r"\bking beds?\b",
            r"\b\d+\s+king\b",
            r"\bking room\b",
            r"\bking\b",
        ],
        "queen": [
            r"\bqueen beds?\b",
            r"\b\d+\s+queens?\b",
            r"\bqueen room\b",
            r"\bqueen\b",
        ],
        "twin": [
            r"\btwin beds?\b",
            r"\b\d+\s+twin\b",
            r"\btwin room\b",
            r"\btwin single use\b",
            r"\b\d+\s+single beds?\b",
            r"\bsingle beds?\b",
            r"\btwin\b",
        ],
        "double": [
            r"\bdouble beds?\b",
            r"\b\d+\s+double\b",
            r"\bfull double bed\b",
            r"\bdouble room\b",
            r"\bdouble single use\b",
        ],
    }

    for bed_type, patterns in bed_patterns.items():
        if any(
            re.search(pattern, room_name)
            for pattern in patterns
        ):
            return bed_type

    return "unknown"

def get_bedroom_count(room_name: str) -> int | None:
    room_name = normalize_room_name(room_name)

    word_numbers = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }

    # 1) Compound form: "2 bedroom" / "2 bedrooms"
    digit_match = re.search(r"\b(\d+)\s*bedrooms?\b", room_name)
    if digit_match:
        return int(digit_match.group(1))

    # 2) Supplier split form: "2 bed room" (e.g. "COLONEL WITH 2 BED ROOM")
    split_match = re.search(r"\b(\d+)\s*bed\s+room\b", room_name)
    if split_match:
        return int(split_match.group(1))

    # 3) Word-number form: "two bedroom" / "two bedrooms"
    for word, value in word_numbers.items():
        if re.search(rf"\b{word}\s+bedrooms?\b", room_name):
            return value

    return None

def get_view_type(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    if re.search(r"\bno\s+view\b", room_name):
        return "no_view"

    # Specific and compound views must come before generic views.
    view_patterns = {
        "burj_khalifa_fountain": [
            "burj khalifa and fountain view",
            "burj khalifa fountain view",
        ],
        "panoramic_sea": [
            "panoramic sea view",
            "panoramic seaview",
        ],
        "partial_sea": [
            "partial sea view",
            "partial seaview",
            "side sea view",
            "side seaview",
            "side sea",
            "sidesea view",
            "sideseaview",
            "limited sea view",
            "limited seaview",
            "lateral sea view",
            "lateral seaview",
            "sea or side sea view",
            "side sea or sea view",
        ],
        "marina_city": [
            "marina city view",
        ],
        "burj_khalifa": [
            "burj khalifa view",
        ],
        "fountain": [
            "fountain view",
        ],
        "beach": [
            "beach view",
            "beachfront",
            "beach front",
        ],
        "lagoon": [
            "lagoon view",
        ],
        "river": [
            "river view",
        ],
        "eiger": [
            "eiger view",
        ],
        "mountain": [
            "mountain view",
            "mountainside view",
        ],
        "land": [
            "land view",
        ],
        "desert": [
            "desert view",
        ],
        "skyline": [
            "skyline view",
        ],
        "panoramic": [
            "panoramic view",
        ],
        "seafront": [
            "seafront view",
            "seafront",
            "sea front view",
            "sea front",
        ],
        "sea": [
            "sea view",
            "seaview",
            "ocean view",
            "ocean facing view",
            "ocean facing",
        ],
        "garden": [
            "garden view",
        ],
        "city": [
            "city view",
        ],
        "pool": [
            "pool view",
        ],
        "seaside": [
            "sea side",
            "seaside",
        ],
    }

    for view_type, patterns in view_patterns.items():
        if any(pattern in room_name for pattern in patterns):
            return view_type

    # Controlled fallback for view types not yet in our dictionary.
    # Examples:
    # marina view      -> marina
    # golf course view -> golf_course
    # courtyard view   -> courtyard
    view_matches = re.findall(
        r"\b([a-z0-9]+(?:\s+[a-z0-9]+){0,2})\s+view\b",
        room_name,
    )

    non_view_attribute_words = {
        # Room categories
        "apartment",
        "bungalow",
        "cabin",
        "room",
        "studio",
        "suite",
        "villa",

        # Room classes
        "classic",
        "club",
        "comfort",
        "deluxe",
        "executive",
        "luxury",
        "premium",
        "premier",
        "standard",
        "superior",

        # Bed attributes
        "bed",
        "beds",
        "bunk",
        "double",
        "full",
        "king",
        "queen",
        "single",
        "sofa",
        "twin",

        # Generic words
        "a",
        "any",
        "beautiful",
        "best",
        "good",
        "great",
        "guest",
        "nice",
        "stunning",
        "the",
        "with",
    }
    for candidate in reversed(view_matches):
        words = candidate.split()

        # Keep only the phrase after connectors.
        # "beds and marina" becomes "marina".
        for connector in ("and", "or", "with"):
            if connector in words:
                words = words[words.index(connector) + 1:]

        words = [
            word
            for word in words
            if word not in non_view_attribute_words
            and not word.isdigit()
        ]

        if words:
            return "_".join(words)

    return "unknown"


def has_balcony(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)
    # Treat "terrace" as a balcony-equivalent outdoor space; suppliers use
    # either word for the same amenity.
    return ("balcony" in room_name) or ("terrace" in room_name)


def has_terrace(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)
    return "terrace" in room_name


def get_dormitory_bed_count(room_name: str) -> int | None:
    room_name = normalize_room_name(room_name)

    # Only meaningful for actual dormitory rooms. Without this guard the
    # pattern would match "1 King Bed" / "2 Beds" in any room name and
    # poison downstream grouping.
    if "dormitory" not in room_name:
        return None

    match = re.search(r"\b(\d+)\s*bed\b", room_name)

    if match:
        return int(match.group(1))

    return None

def get_dormitory_type(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    if "dormitory" not in room_name:
        return "not_applicable"

    dormitory_types = {
        "mixed": ["mixed dormitory"],
        "female": ["female dormitory", "women dormitory"],
        "male": ["male dormitory", "men dormitory"],
    }

    for dormitory_type, keywords in dormitory_types.items():
        if any(keyword in room_name for keyword in keywords):
            return dormitory_type

    return "unknown"

def get_bed_configuration(room_name: str) -> list[dict]:
    room_name = normalize_room_name(room_name)
    # Remove adjacent duplicated supplier bed phrases.
    # Example:
    # "1 king bed 1 king bed" -> "1 king bed"
    #
    # A connector such as "and" prevents removal:
    # "1 king bed and 1 king bed" remains unchanged because it may
    # genuinely describe two separate beds.
    duplicated_bed_phrase_pattern = re.compile(
        r"\b(?P<bed_phrase>"
        r"\d+\s+"
        r"(?:"
        r"king|queen|twin|double|single|"
        r"(?:twin\s+)?bunk|"
        r"(?:single\s+|twin\s+|double\s+)?sofa"
        r")\s+beds?"
        r")"
        r"(?:\s+(?P=bed_phrase))+\b"
    )

    room_name = duplicated_bed_phrase_pattern.sub(
        r"\g<bed_phrase>",
        room_name,
    )

    patterns = [
        ("king", r"\b(\d+)\s+king\b"),
        ("queen", r"\b(\d+)\s+queen\b"),
        ("twin", r"\b(\d+)\s+twin(?!\s+sofa)\s+beds?\b"),
        ("double", r"\b(\d+)\s+double beds?\b"),
        ("single", r"\b(\d+)\s+single(?!\s+sofa)\s+beds?\b"),
        ("bunk", r"\b(\d+)\s+(?:twin\s+)?bunk\s+beds?\b"),
        (
            "sofa",
            r"\b(\d+)\s+(?:single\s+|twin\s+|double\s+)?sofa\s+beds?\b",
        ),
    ]

    found: list[tuple[int, dict]] = []

    # Supplier shorthand:
    # "DOUBLE Double Land View" can mean 2 Double beds.
    if re.search(r"\bdouble\s+double\b", room_name):
        return [
            {
                "type": "double",
                "count": 2,
            }
        ]

    if re.search(r"\btwin\s+twin\b", room_name):
        return [
            {
                "type": "twin",
                "count": 2,
            }
        ]

    # Beds with explicit counts, for example:
    # 1 King, 2 Queen, 2 Twin Beds, 1 Sofa Bed
    for bed_type, pattern in patterns:
        for match in re.finditer(pattern, room_name):
            found.append(
                (
                    match.start(),
                    {
                        "type": bed_type,
                        "count": int(match.group(1)),
                    },
                )
            )

    # `1 King and 1 Single` — a single bed listed without the word "bed"
    # next to it. Only runs when the same digit isn't already accounted
    # for by an adjacent "single bed" / "king" / "double" / etc. match.
    orphan_patterns = [
        ("single", r"\b(\d+)\s+single\b(?! bed)"),
        ("double", r"\b(\d+)\s+double\b(?! bed)"),
        ("twin", r"\b(\d+)\s+twin\b(?! bed)"),
    ]
    for bed_type, pattern in orphan_patterns:
        for match in re.finditer(pattern, room_name):
            entry = (match.start(), {"type": bed_type, "count": int(match.group(1))})
            # Dedupe against any neighbouring bed of the same type.
            if not any(
                abs(existing[0] - entry[0]) <= 6 and existing[1]["type"] == bed_type
                for existing in found
            ):
                found.append(entry)

    # Handle alternatives such as "King or Twin"
    if not found:
        alternatives = [
            (
                r"\bking\s+or\s+twin\b",
                ["king", "twin"],
            ),
            (
                r"\bdouble\s+or\s+twin\b",
                ["double", "twin"],
            ),
            (
                r"\bking\s+or\s+queen\b",
                ["king", "queen"],
            ),
            (
                r"\bqueen\s+or\s+twin\b",
                ["queen", "twin"],
            ),
            # "Twin/Double Room", "Double or Twin", "Twin / Double" — the
            # supplier is signalling that the room can be set up either
            # way. Capture both bed types.
            (
                r"\btwin\s*[/-]\s*double\b",
                ["twin", "double"],
            ),
            (
                r"\bdouble\s*[/-]\s*twin\b",
                ["double", "twin"],
            ),
            (
                r"\bdouble\s+twin\b",
                ["double", "twin"],
            ),
            (
                r"\btwin\s+double\b",
                ["twin", "double"],
            ),
        ]

        for pattern, bed_types in alternatives:
            match = re.search(pattern, room_name)

            if match:
                for offset, bed_type in enumerate(bed_types):
                    found.append(
                        (
                            match.start() + offset,
                            {
                                "type": bed_type,
                                "count": None,
                            },
                        )
                    )

                break


    # Handle bed names without numeric counts.
    # An explicitly singular phrase such as "King Bed"
    # safely implies one bed.
    if not found:
        unnumbered_patterns = [
            ("king", r"\bking bed\b", 1),
            ("queen", r"\bqueen bed\b", 1),
            ("double", r"\bdouble bed\b", 1),
            ("single", r"\bsingle bed\b", 1),
            ("twin", r"\btwin bed\b", 1),
            ("bunk", r"\bbunk bed\b", 1),
            ("sofa", r"\bsofa bed\b", 1),

            # Bare room-label wording identifies the bed type,
            # but does not safely establish its count.
            ("king", r"\bking\b", None),
            ("queen", r"\bqueen\b", None),
            ("twin", r"\btwin\b", None),
        ]

        for bed_type, pattern, count in unnumbered_patterns:
            for match in re.finditer(pattern, room_name):
                if any(
                    existing[1]["type"] == bed_type
                    for existing in found
                ):
                    continue

                found.append(
                    (
                        match.start(),
                        {
                            "type": bed_type,
                            "count": count,
                        },
                    )
                )
    # Final fallback: when the supplier wrote the bed name without the
    # word "bed" or any count (e.g. "Le Meridien Club Skyline Room
    # Double", "Skyline Club Twin"), capture the bare bed type so the
    # matcher has a bed signal at all. Only fires when nothing else was
    # captured — guards against false positives in names like "Deluxe
    # Double Room" where "double" refers to the bed layout, not a count.
    if not found:
        for bed_type in ("double", "twin"):
            match = re.search(rf"\b{bed_type}\b", room_name)
            if match:
                found.append(
                    (
                        match.start(),
                        {"type": bed_type, "count": None},
                    )
                )

    found.sort(key=lambda item: item[0])

    return [
        bed
        for _, bed in found
    ]

def has_club_access(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)

    club_access_keywords = [
        "club level",
        "club lounge access",
        "club access",
        "club millesime access",
        "club millésime access",
        # The bare "club" prefix is enough to imply a club-tier room
        # (e.g. "Club Room", "Club Suite", "CLUB SKYLINE VIEW"). The
        # matcher enforces club_access equality, so this also keeps a
        # plain "Superior Room" from being merged with "Club Superior".
        "club room",
        "club suite",
    ]

    # Treat a leading or standalone "club" as a club-tier room.
    has_bare_club = (
        room_name.startswith("club ")
        or " club " in f" {room_name} "
        or room_name == "club"
    )

    return any(
        keyword in room_name
        for keyword in club_access_keywords
    ) or has_bare_club


def has_connecting_room(room_name: str) -> bool:
    """
    True if the room name describes a connecting (interlocking) room.

    A connecting room only makes sense in combination with another room —
    it is not the same physical product as a non-connecting equivalent.
    The matcher uses this to keep them in separate groups.
    """
    room_name = normalize_room_name(room_name)
    return "connecting" in room_name

def has_swim_up(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)

    return (
        "swim up" in room_name
        or "swimup" in room_name
    )
def has_annex(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)

    return (
        "annex" in room_name
        or "anex" in room_name
    )
def has_jacuzzi(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)
    return "jacuzzi" in room_name


def has_hot_tub(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)
    return "hot tub" in room_name

def has_uncertain_bed_assignment(room_name: str) -> bool:
    text = room_name.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    uncertain_patterns = [
        r"\bbed type is subject to availability\b",
        r"\broom type assigned on arrival\b",
        r"\broom assigned on arrival\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in uncertain_patterns
    )

def get_bed_relation(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    # Alternative layouts
    if (
        " or " in f" {room_name} "
        or re.search(r"\bdouble\s+twin\b", room_name)
        or re.search(r"\btwin\s+double\b", room_name)
    ):
        return "alternative"

    # Combined layouts
    if " and " in f" {room_name} ":
        return "combined"

    return "unknown"

def has_pool_access(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)

    pool_access_patterns = [
        r"\bpool access\b",
        r"\bdirect pool access\b",
        r"\bprivate pool access\b",
        r"\bshared pool access\b",
        r"\bswim up\b",
        r"\bswimup\b",
    ]

    return any(
        re.search(pattern, room_name)
        for pattern in pool_access_patterns
    )

def has_luxury_variant(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)
    return bool(re.search(r"\bluxury\b", room_name))


def has_overwater(room_name: str) -> bool:
    room_name = normalize_room_name(room_name)

    return bool(
        re.search(
            r"\b(?:overwater|over water|water villa)\b",
            room_name,
        )
    )
def get_building_block(room_name: str) -> str | None:
    """
    Extract an explicit hotel building/block identifier.

    Examples:
    B Block       -> b
    Block B       -> b
    Block 2 Room  -> 2
    Bungalow      -> None
    """
    normalized_name = room_name.lower()

    patterns = [
        r"\b([a-z0-9]+)\s+block\b",
        r"\bblock\s+([a-z0-9]+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_name)

        if match:
            return match.group(1)

    return None

def extract_features(room_name: str) -> dict:
    category = get_room_category(room_name)
    room_class = get_room_class(room_name)

    # Class-only supplier names such as "DELUXE" mean "Deluxe Room".
    if category == "unknown" and room_class != "unknown":
        category = "room"

    return {
        "identity_tokens": get_identity_tokens(room_name),
        "category": category,
        "room_class": room_class,

        "building_block": get_building_block(room_name),
        "suite_type": get_suite_type(room_name),
        "layout": get_layout(room_name),
        "luxury_variant": has_luxury_variant(room_name),
        "overwater": has_overwater(room_name),
        "club_access": has_club_access(room_name),
        "view": get_view_type(room_name),
        "balcony": has_balcony(room_name),
        "terrace": has_terrace(room_name),
        "dormitory_bed_count": get_dormitory_bed_count(room_name),
        "dormitory_type": get_dormitory_type(room_name),
        "bed_type": get_bed_type(room_name),
        "bedroom_count": get_bedroom_count(room_name),
        "bed_configuration": get_bed_configuration(room_name),
        "connecting_room": has_connecting_room(room_name),
        "swim_up": has_swim_up(room_name),
        "pool_access": has_pool_access(room_name),
        "annex": has_annex(room_name),
        "jacuzzi": has_jacuzzi(room_name),
        "hot_tub": has_hot_tub(room_name),
        "occupancy": get_occupancy(room_name),
        "single_use": is_single_use(room_name),
        "bed_relation": get_bed_relation(room_name),
        "bed_assignment_uncertain": has_uncertain_bed_assignment(room_name),
    }