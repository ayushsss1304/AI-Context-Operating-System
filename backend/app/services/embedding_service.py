import hashlib
import math
import re


EMBEDDING_DIMENSIONS = 384
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


class EmbeddingService:
    """Small local embedding fallback based on feature hashing.

    This keeps the MVP self-contained while preserving the same data flow as a
    provider-backed embedding model: text in, vector out, cosine similarity for
    retrieval. The stored vector can be migrated to pgvector later without
    changing the memory API surface.
    """

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * EMBEDDING_DIMENSIONS
        tokens = TOKEN_PATTERN.findall(text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSIONS
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        return self._normalize(vector)

    def similarity(self, left: list[float] | None, right: list[float] | None) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        return sum(a * b for a, b in zip(left, right))

    def _normalize(self, vector: list[float]) -> list[float]:
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0.0:
            return vector
        return [value / magnitude for value in vector]
