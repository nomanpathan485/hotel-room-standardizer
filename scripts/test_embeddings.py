import ollama

response = ollama.embed(
    
    model="nomic-embed-text",
    input=[
        "Deluxe King Room",
        "King Deluxe Room"
    ]
)
from sklearn.metrics.pairwise import cosine_similarity

embeddings = response["embeddings"]

score = cosine_similarity(
    [embeddings[0]],
    [embeddings[1]]
)

print(score)

print(len(response["embeddings"]))
print(len(response["embeddings"][0]))