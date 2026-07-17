import re

from app.services.normalizer import normalize_room_name


def get_room_category(room_name: str) -> str:
    room_name = normalize_room_name(room_name)

    # Order matters: first match wins. Compound categories (e.g. "suite")
    # come before their bare word (e.g. "duplex suite" -> suite, not duplex).
    # Patterns are anchored as compound phrases ("triple room") or as
    # standalone words at the start of the name to avoid catching bed
    # descriptions like "1 Single Sofa Bed" or "2 Twin Beds".
    #
    # `single room` is intentionally NOT a category: a name like
    # "Deluxe 1 Single Room with 1 King Bed" describes a room with a single
    # bed in it, not a single-occupancy room category. Single-occupancy
    # rooms are extremely rare in the dataset and the bed-quantity is more
    # useful as a bed_type / bed_configuration signal.
    categories = {
        "dormitory": ["dormitory"],
        "family": ["family room", "family"],
        "quadruple": ["quadruple", "quad room"],
        "triple": ["triple room"],
        "suite": ["suite"],
        "studio": ["studio"],
        "penthouse": ["penthouse"],
        "duplex": ["duplex"],
        "loft": ["loft"],
        "chalet": ["chalet"],
        "cabin": ["cabin"],
        "cabana": ["cabana"],
        "bungalow": ["bungalow"],
        "villa": ["villa"],
        "apartment": ["apartment"],
        "annex": ["annex"],
    }

    for category, keywords in categories.items():
        if any(keyword in room_name for keyword in keywords):
            return category

    return "room"

def get_room_class(room_name: str) -> str:
    room_name = normalize_room_name(room_name)
    # Defensive: even though the normalizer strips "standard rate", make
    # sure a residual substring cannot turn a Club/Superior room into a
    # Standard room by accident. The literal phrase `standard rate` (or
    # `standard bedroom`) is a supplier phrase, not a room class.
    room_class_blocklist = {"standard"}
    if "standard rate" in room_name or "standard bedroom" in room_name:
        # Treat the rest of the string as if `standard` were not a class.
        room_name = room_name.replace("standard rate", " ")
        room_name = room_name.replace("standard bedroom", " ")
    room_classes = {
        "standard": ["standard"],
        "superior": ["superior"],
        "deluxe": ["deluxe"],
        "premium": ["premium"],
        "executive": ["executive"],
        "club": ["club"],
        "classic": ["classic"],
        "comfort": ["comfort"],
        "business": ["business"],
        "luxury": ["luxury"],
        "prestige": ["prestige"],
        "signature": ["signature"],
        "grand": ["grand"],
        "presidential": ["presidential"],
        "royal": ["royal"],
        "premier": ["premier"],
        "panoramic": ["panoramic"],
        "diplomatic": ["diplomatic"],
    }
    for room_class, keywords in room_classes.items():
        if any(keyword in room_name for keyword in keywords):
            return room_class
    return "unknown"

def get_suite_type(room_name: str) -> str:
    room_name = normalize_room_name(room_name)
    if "suite" not in room_name:
        return "not_applicable"
    suite_types = {
        "presidential": ["presidential suite"],
        "royal": ["royal suite"],
        "junior": ["junior suite"],
        "senior": ["senior suite"],
        "family": ["family suite"],
        "prestige": ["prestige suite"],
        "emirates": ["emirates suite"],
        "signature": ["signature suite"],
        "honeymoon": ["honeymoon suite"],
        "bridal": ["bridal suite"],
        "penthouse": ["penthouse suite"],
        "duplex": ["duplex suite"],
    }
    for suite_type, keywords in suite_types.items():
        if any(keyword in room_name for keyword in keywords):
            return suite_type
    return "standard"

def get_bed_type(room_name: str) -> str:
    if re.search(r"\bdouble\s+twin\b", room_name):
        print("MATCHED DOUBLE_OR_TWIN")
        return "double_or_twin"
    if re.search(r"\btwin\s+double\b", room_name):
        print("MATCHED DOUBLE_OR_TWIN")
        return "double_or_twin"

    # Bed style has priority over bed size.
    if re.search(r"\bbunk beds?\b", room_name):
        return "bunk"
    if re.search(r"\bsofa beds?\b", room_name) and not re.search(
        r"\b(?:king|queen|double|twin|single)\s+bed\b", room_name
    ):
        return "sofa"
    bed_patterns = {
        "king": [
            r"\bking beds?\b",
            r"\b1 king\b",
            r"\b2 king\b",
            r"\bking room\b",
            r"\bking\b",
        ],
        "queen": [
            r"\bqueen beds?\b",
            r"\b1 queen\b",
            r"\b2 queen\b",
            r"\bqueen room\b",
            r"\bqueen\b",
        ],
        "twin": [
            r"\btwin beds?\b",
            r"\b2 twin\b",
            r"\btwin room\b",
            r"\btwin single use\b",
            r"\b2 single beds?\b",
            r"\bsingle beds?\b",
            r"\btwin\b",
        ],
        "double": [
            r"\bdouble beds?\b",
            r"\b1 double\b",
            r"\bfull double bed\b",
            r"\bdouble room\b",
            r"\bdouble single use\b",
            r"\bdouble\b",
        ],
    }
    for bed_type, patterns in bed_patterns.items():
        if any(re.search(pattern, room_name) for pattern in patterns):
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

    # "(No View)" / "no view" should never resolve to a positive view.
    if re.search(r"\bno\s+view\b", room_name):
        return "no_view"

    # Order matters: compound / specific views must come before generic
    # ones (e.g. "panoramic sea view" must win over "sea view").
    view_patterns = {
        "burj_khalifa_fountain": [
            "burj khalifa and fountain view",
            "burj khalifa fountain view",
        ],
        "partial_sea": [
            "partial sea view",
            "partial seaview",
            "side sea view",
            "side seaview",
            "limited sea view",
            "limited seaview",
        ],

        "lateral_sea": [
            "lateral sea view",
            "lateral seaview",
        ],
        "panoramic_sea": [
            "panoramic sea view",
            "panoramic seaview",
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
        "ocean": [
            "ocean view",
            "ocean facing view",
            "ocean facing",
            "ocean",
        ],
        "beach": [
            "beach view",
            "beachfront",
            "beach front",
        ],
        "lagoon": [
            "lagoon view",
            "lagoon",
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
            "mountain",
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
        "sea": [
            "sea view",
            "seaview",
        ],
        "garden": [
            "garden view",
            "garden",
        ],
        "city": [
            "city view",
        ],
        "pool": [
            "pool view",
        ],
        
    }

    for view_type, patterns in view_patterns.items():
        if any(pattern in room_name for pattern in patterns):
            return view_type

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

    patterns = [
        ("king", r"\b(\d+)\s+king\b"),
        ("queen", r"\b(\d+)\s+queen\b"),
        ("twin", r"\b(\d+)\s+twin beds?\b"),
        ("double", r"\b(\d+)\s+double beds?\b"),
        ("single", r"\b(\d+)\s+single beds?\b"),
        ("bunk", r"\b(\d+)\s+(?:twin\s+)?bunk\s+beds?\b"),
        (
            "sofa",
            r"\b(\d+)\s+(?:single\s+|twin\s+|double\s+)?sofa\s+beds?\b",
        ),
    ]

    found: list[tuple[int, dict]] = []

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


# Handle bed names without explicit counts.
# Examples:
# "Deluxe King Room"
# "King and Single Bed"
    if not found:
        unnumbered_patterns = [
            ("king", r"\bking\b"),
            ("queen", r"\bqueen\b"),
            ("twin", r"\btwin\b"),
            ("double", r"\bdouble bed\b"),
            ("single", r"\bsingle bed\b"),
            ("bunk", r"\bbunk bed\b"),
            ("sofa", r"\bsofa bed\b"),
        ]

        for bed_type, pattern in unnumbered_patterns:
            for match in re.finditer(pattern, room_name):
                found.append(
                    (
                        match.start(),
                        {
                            "type": bed_type,
                            "count": None,
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

def extract_features(room_name: str) -> dict:
    return {
        "category": get_room_category(room_name),
        "room_class": get_room_class(room_name),
        "suite_type": get_suite_type(room_name),
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
        "swim_up":has_swim_up(room_name), 
        "annex": has_annex(room_name),
        "jacuzzi": has_jacuzzi(room_name),
        "hot_tub": has_hot_tub(room_name),
    }
