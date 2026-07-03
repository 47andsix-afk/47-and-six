import importlib.util
import sys

chromadb = None
if importlib.util.find_spec("chromadb"):
    try:
        import chromadb as chromadb_module

        chromadb = chromadb_module
    except Exception:
        chromadb = None


def _is_venv_python() -> bool:
    return bool(sys.prefix) and (".venv" in sys.prefix or "venv" in sys.prefix)


def main() -> None:
    if chromadb is None:
        print("chromadb is not installed; skipping matrix build.")
        return

    if _is_venv_python():
        print(f"Using virtual environment Python: {sys.executable}")

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="operational_matrix")

    rules = [
        {
            "id": "CE160",
            "text": "CE160 Culinary Entrepreneurship: Apply strict cost control, customer communication discipline, and scalable business strategy.",
        },
        {
            "id": "CE167",
            "text": "CE167 Purchasing & Cost Control: Track ingredient waste, maintain vendor relationships, and reconcile costs at the end of each service block.",
        },
        {
            "id": "CE187",
            "text": "CE187 Menu Design & Management: Build menus based on seasonality, profitability, customer profile, and operational efficiency.",
        },
        {
            "id": "CU101",
            "text": "CU101 Culinary Foundations: Maintain classical technique, sanitation discipline, knife skills, and foundational cooking methods.",
        },
        {
            "id": "CU122",
            "text": "CU122 Culinary Arts & Patisserie: Execute precise timing, temperature control, and advanced pastry techniques.",
        },
        {
            "id": "CU132",
            "text": "CU132 World Cuisines: Integrate global flavor profiles with local El Paso ingredients and cultural authenticity.",
        },
        {
            "id": "CU222",
            "text": "CU222 Farm to Table Kitchen: Prioritize local sourcing, sustainability, ingredient transparency, and farm-to-table ethics.",
        },
        {
            "id": "OR120",
            "text": "OR120 Orientation: Maintain professionalism, communication standards, and adherence to Escoffier operational expectations.",
        },
    ]

    collection.add(
        ids=[r["id"] for r in rules],
        documents=[r["text"] for r in rules],
        metadatas=[{"course": r["id"]} for r in rules],
    )

    print("Operational matrix initialized with", len(rules), "rules.")


if __name__ == "__main__":
    main()
