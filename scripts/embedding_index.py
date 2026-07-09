import ollama
from sklearn.metrics.pairwise import cosine_similarity
from app.services.normalizer import normalize_room_name
from app.database import SessionLocal
from app.models import Room


# Create a database session
db = SessionLocal()

# Load all rooms from the database
rooms = db.query(Room).all()

print(f"Loaded {len(rooms)} rooms")

# Extract only the room names into a list
room_names = [
    normalize_room_name(room.supplier_room_name)
    for room in rooms
]

# Generate embeddings for all room names in one request (batching)
response = ollama.embed(
    model="nomic-embed-text",
    input=room_names
)

# Dictionary to store: room_id -> embedding
embedding_index = {}

# Pair each room with its embedding and store it
for room, embedding in zip(rooms, response["embeddings"]):
    embedding_index[room.id] = embedding

print(f"Generated embeddings: {len(embedding_index)}")
query = normalize_room_name("Twin Room")

# Generate embedding for the query
query_embedding = ollama.embed(
    model="nomic-embed-text",
    input=query
)["embeddings"][0]

results = []

# Compare the query with every room
for room in rooms:
    score = cosine_similarity(
        [query_embedding],
        [embedding_index[room.id]]
    )[0][0]

    # Store both the room name and its similarity score
    results.append((room.id, room.supplier_room_name, score))

# Sort by score in descending order
results.sort(key=lambda x: x[1], reverse=True)

print(f"\nQuery: {query}\n")

# Print the top 5 matches
for room_id, room_name, score in results[:5]:
    print(f"{room_id} | {room_name} --> {score:.4f}")