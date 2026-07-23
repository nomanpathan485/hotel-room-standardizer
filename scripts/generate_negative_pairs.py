from app.services.dataset_store import load_benchmark_case
from app.services.training_pair_generator import (
    deduplicate_pairs,
    generate_hard_negative_pairs,
)


CASE_ID = "hotel_39766989_20260722_173629"


# Load one saved benchmark case
case = load_benchmark_case(CASE_ID)


# Generate all hard negative pairs
raw_pairs = generate_hard_negative_pairs(
    input_data=case["input"],
    vervotech_response=case["vervotech"],
)


# Remove duplicate room-name pairs
pairs = deduplicate_pairs(raw_pairs)


# Show how much duplicate data was removed
print(f"Before deduplication: {len(raw_pairs)}")
print(f"After deduplication: {len(pairs)}")


# Inspect the first 10 examples
print("\nFirst 10 hard negative pairs:\n")

for pair in pairs[:10]:
    print(pair)