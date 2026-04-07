from __future__ import annotations

from typing import Iterable, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np


class TextEmbedder:
    """Simple local embedder based on TF-IDF for portfolio/demo use.

    This keeps the project fully runnable without external APIs.
    If you later want a stronger semantic layer, swap this with OpenAI,
    sentence-transformers, or another embedding provider.
    """

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_features=2048,
        )

    def fit_transform(self, texts: Iterable[str]) -> np.ndarray:
        matrix = self.vectorizer.fit_transform(list(texts))
        dense = matrix.toarray()
        return normalize(dense)

    def transform(self, texts: Iterable[str]) -> np.ndarray:
        matrix = self.vectorizer.transform(list(texts))
        dense = matrix.toarray()
        return normalize(dense)
