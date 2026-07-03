import chromadb

# Initialize the local persistent vector database
client = chromadb.PersistentClient(path="./chroma_db")

# Create or load the 47-&-SIX operational memory collection
collection = client.get_or_create_collection(name="operational_matrix")

# Inject baseline 6-Minute Economy and routing parameters
collection.upsert(
    documents=[
        "The CU132 protocol dictates scaling menus from 10 to 500 covers based on the 6-minute interval.",
        "For catering inquiries, route to CU132 and request date and headcount.",
        "47-&-SIX operations are based in El Paso, TX. Regional operational radius is active.",
        "Extended operational radius includes New Mexico (NM) strictly for large-scale CU132 catering events. An out-of-region logistics surcharge applies to all NM commissions."
    ],
    metadatas=[
        {"category": "scaling"}, 
        {"category": "routing"}, 
        {"category": "location"},
        {"category": "logistics"}
    ],
    ids=["rule_1", "rule_2", "rule_3", "rule_4"]
)

print("Memory matrix updated. New Mexico logistics protocol injected.")