from app.services.dataset_store import load_benchmark_case
from app.services.training_pair_generator import (
    deduplicate_pairs,
    generate_positive_pairs,
)


CASE_ID = "hotel_39766989_20260722_173629"


case = load_benchmark_case(CASE_ID)

raw_pairs = generate_positive_pairs(
    input_data=case["input"],
    vervotech_response=case["vervotech"],
)

pairs = deduplicate_pairs(raw_pairs)

print(f"Before deduplication: {len(raw_pairs)}")
print(f"After deduplication: {len(pairs)}")

print("\nFirst 10 positive pairs:\n")

for pair in pairs[:10]:
    print(pair)