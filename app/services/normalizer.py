import html
import re
NORMALIZATION_ALIASES = {
    r"\bde\s+luxe\b": "deluxe",
    r"\bdlx\b": "deluxe",
    r"\bstd\b": "standard",
    r"\bsup\b": "superior",
}
NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}

# Supplier-rate noise that the matcher/feature extractor should never see.
# These phrases are added by rate-shopping systems (board basis, occupancy,
# supplier tags) and add no information about the physical room.
_NOISE_PHRASES = [
    r"doubleplus\d+children",
    r"opaque rate",
    r"standard rate",
    r"max \d+",
    r"\d+\s*ad",
    r"\d+\s*ch",
    r"bed and breakfast",
    r"breakfast",
    r"package rate",
    # Cancellation-policy noise
    r"\bnon[\s-]?refundable\b",
    r"\brefundable rate\b",
    r"\bfree cancellation\b",
    r"\bflexible cancellation\b",
    r"\bfully flexible\b",
    r"\bspecial conditions\b",

    # Payment-policy noise
    r"\bno prepayment needed\b",
    r"\bno prepayment required\b",
    r"\bprepayment required\b",
    r"\bpay at the property\b",
    r"\bpay at property\b",
    r"\bpay at the hotel\b",
    r"\bpay at hotel\b",
    r"\bpay on arrival\b",
    r"\bpay now\b",
    r"\bpay later\b",
    r"\breserve now pay later\b",
    r"\bbook now pay later\b",

    # Tax and fee noise
    r"\bcity tax included\b",
    r"\bcity tax excluded\b",
    r"\btourist tax included\b",
    r"\btourist tax excluded\b",
    r"\btaxes included\b",
    r"\btaxes excluded\b",
    r"\btaxes and fees included\b",
    r"\btaxes and fees excluded\b",
    r"\bvat included\b",
    r"\bvat excluded\b",
    r"\bservice charge included\b",
    r"\bservice charge excluded\b",

    # Promotional-rate noise
    r"\badvance purchase\b",
    r"\bearly bird\b",
    r"\blast minute deal\b",
    r"\bspecial offer\b",
    r"\bpromotional rate\b",
    r"\bpromo rate\b",
    r"\bmobile rate\b",
    r"\bmobile deal\b",
    r"\bmember rate\b",
    r"\bmember deal\b",
    r"\bweb rate\b",
    r"\bonline rate\b",
    r"\bbest available rate\b",
    r"\blimited time offer\b",
    r"\bsecret deal\b",
    r"happy hour",
    r"afternoon tea",
    r"\bnon\s*smoking\b",
    r"\bno\s*smoking\b",
    r"\bsmoking\b",
    r"extra beds?",
    r"extra\s*bed",
    r"bed type is subject[^.]*(?:\.|$)",
    r"\(subject to availability\)",
    r"subject to availability",
    # Double-encoded `&` from a supplier bug: "AMP;AMP;" is what
    # "&&" or "&amp;amp;" became after one round of decoding.
    r"\bamp;amp;",
]

_NOISE_RE = re.compile("|".join(_NOISE_PHRASES), re.IGNORECASE)


def normalize_room_name(room_name: str) -> str:
    """
    Normalize a supplier room name for grouping and feature extraction.
    """
    if not room_name:
        return ""

    text = html.unescape(room_name)
    text = text.lower()
    # Standardize supplier number formats.
    # Example: "Two Twin Beds" -> "2 Twin Beds"
    text = re.sub(
        r"\b(" + "|".join(NUMBER_WORDS) + r")\b",
        lambda match: NUMBER_WORDS[match.group(0)],
        text,
    )
    # Separate joined digit-letter tokens used by suppliers.
    # Examples: 02DELUXE -> 02 deluxe, 2Bedroom -> 2 bedroom, KING1 -> king 1
    text = re.sub(r"(?<=\d)(?=[a-z])", " ", text)
    text = re.sub(r"(?<=[a-z])(?=\d)", " ", text)
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = " ".join(text.split())

   
    for pattern, replacement in NORMALIZATION_ALIASES.items():
        text = re.sub(pattern, replacement, text)

    text = _NOISE_RE.sub(" ", text)
    text = " ".join(text.split())

    return text