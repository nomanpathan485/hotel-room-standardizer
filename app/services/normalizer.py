import re


def normalize_room_name(room_name: str) -> str:
    room_name = room_name.lower()
    room_name = room_name.replace("-", " ")
    room_name = re.sub(r"[^a-z0-9 ]", " ", room_name)
    room_name = " ".join(room_name.split())
    return room_name

    """
    Normalize the room name by converting it to lowercase, removing punctuation,
    and stripping leading/trailing whitespace.
    """
   
   