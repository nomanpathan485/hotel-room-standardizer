# Room Standardization Experiments

---

# Experiment 1

## Title

RapidFuzz Similarity Evaluation

---

## Objective

Evaluate RapidFuzz scorers for hotel room-name similarity.

---

## Dataset

103 hotel room names.

---

## Test Case

Room 1

King Deluxe Room

Room 2

Deluxe King Room

Expected

These should be considered the same room.

---

## Algorithms Tested

1. ratio()
2. token_sort_ratio()
3. token_set_ratio()

---

## Results

ratio()

68.75

token_sort_ratio()

100

token_set_ratio()

100

---

## Observation

ratio() is sensitive to word order.

token_sort_ratio() correctly handles reordered words.

token_set_ratio() also correctly handles reordered words.

---

## Conclusion

token_sort_ratio() and token_set_ratio() appear to be much better candidates for hotel room-name matching than ratio().

More experiments are required before selecting the final algorithm.

---

# Planned Experiments

Experiment 2

Run RapidFuzz against the complete dataset.

---

Experiment 3

Rule-based standardization.

---

Experiment 4

Sentence Embeddings (MiniLM)

---

Experiment 5

BGE Embeddings

---

Experiment 6

E5 Embeddings

---

Experiment 7

Local LLM (Qwen/Llama)

---

# Final Evaluation

Each approach will be evaluated on:

- Accuracy
- Latency
- Memory Usage
- Ease of Deployment
- Cost

The goal is to determine whether a local solution can replace or reduce dependence on Vervotech for hotel room-name standardization.