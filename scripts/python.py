from app.services.feature_extractor import (extract_features, get_occupancy, get_room_class)
from app.services.pair_feature_extractor import extract_pair_features
from app.services.normalizer import normalize_room_name
print(normalize_room_name("DLX Room"))
print(normalize_room_name("STD Room"))
print(normalize_room_name("SUP Room"))
print(get_room_class("DLX Room"))
print(get_room_class("STD Room"))
print(get_room_class("SUP Room"))