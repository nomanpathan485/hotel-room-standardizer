import ollama


def generate_canonical_name(room_names: list[str]) -> str:
    group_text = "\n".join(f"- {name}" for name in room_names)

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert hotel room naming assistant.\n"
                    "You will receive multiple supplier room names that have "
                    "already been confirmed as equivalent.\n"
                    "Generate one canonical room name for the entire group.\n\n"
                    "Rules:\n"
                    "- Preserve meaningful room attributes such as Standard, "
                    "Deluxe, Superior, Executive, Family, Suite, Studio, "
                    "Dormitory, Twin, Double, King, and Queen.\n"
                    "- Preserve meaningful views such as Garden View, Sea View, "
                    "City View, or Pool View.\n"
                    "- Remove occupancy text such as 2 Adults, 2 Children, "
                    "Sleeps 4, and Single Use.\n"
                    "- Remove smoking information and supplier formatting noise.\n"
                    "- Preserve dormitory capacity such as 6-Bed or 8-Bed.\n"
                    "- Remove ordinary bed counts only when they are supplier-detail noise.\n"
                    "- Never add information that is not present in the names.\n"
                    "- Return exactly one concise canonical room name.\n"
                    "- Return one line only.\n"
                    "- Do not explain."
                    "- Use only attributes that describe the shared identity of the entire group.\n"
                    "- Do not include optional details that appear in only some supplier names.\n"
                    "- For dormitories, preserve the dormitory bed count and gender type when present.\n"
                    "- Prefer names like 'Bed in 6-Bed Mixed Dormitory'.\n"
                    "- Do not add bunk-bed wording unless it is essential and consistently present across the group.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Equivalent supplier room names:\n"
                    f"{group_text}"
                ),
            },
        ],
    )

    return response["message"]["content"].strip()