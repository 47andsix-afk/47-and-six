import hashlib
from typing import List


class ChefEmbeddings:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vector = [((byte / 255.0) * 2.0) - 1.0 for byte in digest[:32]]
            vectors.append(vector)
        return vectors
