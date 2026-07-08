from rapidfuzz import fuzz

room1 = "King Deluxe Room"
room2 = "Deluxe King Room"

print("Ratio:", fuzz.ratio(room1, room2))
print("Token Sort:", fuzz.token_sort_ratio(room1, room2))
print("Token Set:", fuzz.token_set_ratio(room1, room2))