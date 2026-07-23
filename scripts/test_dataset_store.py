from app.services.dataset_store import load_benchmark_case


case = load_benchmark_case("test_hotel_002")


print("Benchmark loaded successfully.")

print("\nINPUT:")
print(case["input"])

print("\nVERVOTECH:")
print(case["vervotech"])

print("\nOUR V4:")
print(case["our_v4"])