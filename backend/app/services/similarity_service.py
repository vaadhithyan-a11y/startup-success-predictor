import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.ml.data_ingestion import generate_synthetic_data


class SimilarityService:
    def __init__(self):
        self._data = generate_synthetic_data(n_samples=50)
        self._feature_cols = [
            "revenue", "funding_raised", "employees", "burn_rate",
            "market_size", "growth_rate", "founder_experience",
        ]

    def _get_feature_vector(self, idx: int) -> np.ndarray:
        row = self._data.iloc[idx]
        return np.array([row[col] for col in self._feature_cols]).reshape(1, -1)

    def find_similar(self, startup_id: int, n: int = 5) -> list[dict]:
        if startup_id < 0 or startup_id >= len(self._data):
            return []

        target_vec = self._get_feature_vector(startup_id)
        similarities = []

        for i in range(len(self._data)):
            if i == startup_id:
                continue
            vec = self._get_feature_vector(i)
            sim = cosine_similarity(target_vec, vec)[0][0]
            similarities.append({"startup_id": i + 1, "similarity_score": round(float(sim), 4)})

        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similarities[:n]
