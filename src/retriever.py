"""
Historical Resolution Retriever (RAG Grounding) for @AppleSupport.

Indexes historical customer-agent resolution pairs extracted from TWCS and
retrieves the top-k most relevant historical resolutions to ground reply drafting.
"""

import os
import json
import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class HistoricalRetriever:
    """Retrieves historically grounded Apple resolutions using vector similarity."""

    def __init__(self, knowledge_base_path: str = "data/processed/apple_pairs_sampled.jsonl", max_entries: int = 10000):
        self.knowledge_base_path = knowledge_base_path
        self.max_entries = max_entries
        self.records: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=25000,
            sublinear_tf=True,
            stop_words="english"
        )
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        """Loads pairs and fits TF-IDF matrix."""
        if not os.path.exists(self.knowledge_base_path):
            logger.warning(f"Knowledge base file not found at {self.knowledge_base_path}. Using fallback grounding.")
            return

        queries = []
        with open(self.knowledge_base_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= self.max_entries:
                    break
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                self.records.append(item)
                queries.append(item["customer_text"])

        if queries:
            self.tfidf_matrix = self.vectorizer.fit_transform(queries)
            logger.info(f"Retriever indexed {len(self.records)} historical Apple resolution pairs.")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top-k closest historical customer inquiries and Apple's historical responses.
        Returns list of dicts with:
        - customer_text
        - apple_reply
        - similarity_score
        """
        if self.tfidf_matrix is None or not self.records:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(sims)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(sims[idx])
            rec = self.records[idx]
            results.append({
                "customer_text": rec.get("customer_text", ""),
                "apple_reply": rec.get("apple_reply", ""),
                "similarity_score": round(score, 4),
                "tweet_id": rec.get("customer_tweet_id")
            })
        return results


# Default singleton instance cache
_GLOBAL_RETRIEVER = None

def get_retriever() -> HistoricalRetriever:
    global _GLOBAL_RETRIEVER
    if _GLOBAL_RETRIEVER is None:
        _GLOBAL_RETRIEVER = HistoricalRetriever()
    return _GLOBAL_RETRIEVER
