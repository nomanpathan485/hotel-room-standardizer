import html
import re


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
    r"happy hour",
    r"afternoon tea",
    r"non smoking",
    r"no smoking",
    r"smoking",
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
    Normalize a supplier room name for grouping.

    Pipeline:
        1. Decode HTML entities (`&amp;` -> `&`, etc.).
        2. Strip supplier-rate noise phrases (board basis, occupancy, etc.).
        3. Lowercase, replace dashes with spaces, drop punctuation, collapse
           whitespace.

    The result is suitable for keyword/regex feature extraction and for
    token-set fuzzy comparison in the matcher.
    """
    if not room_name:
        return ""

    text = html.unescape(room_name)
    text = _NOISE_RE.sub(" ", text)
    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = " ".join(text.split())
    return text
