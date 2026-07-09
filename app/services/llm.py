import ollama


def generate_canonical_name(room_name: str) -> str:
    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert hotel room standardization assistant.\n"
                    "Convert supplier room names into a single canonical room name.\n\n"
                    "Rules:\n"
                    "- Remove amenities (WiFi, Breakfast, Balcony, View, NonSmoking, Smoking, Accessible, etc.).\n"
                    "- Remove occupancy information (2 Adults, 1 Child, Sleeps 4, etc.).\n"
                    "- Remove room policies.\n"
                    "- Remove marketing words (Best Available, Special Offer, Promo, etc.).\n"
                    "- Keep important room attributes like Deluxe, Superior, Standard, Executive, Suite, Studio, Family, Twin, Double, King, Queen, Single.\n"
                    "- Ignore bed counts like '1 Double Bed' or '2 Twin Beds' unless they define the room type.\n"
                    "- Return only the canonical room name.\n"
                    "- Return only one line.\n"
                    "- Do not explain."
                    "- Never add information that is not present in the input."
                    "- If an attribute is not explicitly mentioned, do not infer or guess it."
                ),
            },
            {
                "role": "user",
                "content": room_name,
            },
        ],
    )

    return response["message"]["content"].strip()