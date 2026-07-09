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

## Progress Update

### Semantic Matching Research

- Integrated Ollama locally.
- Using `nomic-embed-text` for generating embeddings.
- Built an embedding pipeline:
  - Load room names from SQLite.
  - Generate embeddings in a single batch.
  - Store embeddings in memory (`room_id -> embedding`).
- Implemented cosine similarity for semantic room matching.
- Added text normalization before embedding generation, which improved similarity scores.
- Initial testing shows the pipeline works, but `nomic-embed-text` struggles with generic room names (e.g., "ROOM", "STANDARD ROOM").
- Next step is benchmarking better embedding models (BGE-M3, E5, etc.) to compare accuracy, latency, and feasibility as a replacement for the current Vervotech workflow.

### Update

- Implemented semantic search using cosine similarity.
- Added normalization before embedding generation.
- Next optimization: remove duplicate room names before generating embeddings to reduce unnecessary embedding computations.

### Update

- Decided to introduce an evaluation dataset.
- Purpose: compare different matching approaches using the same test cases.
- This will allow objective comparison of RapidFuzz, embedding models, and future LLM-based approaches.