"""
ml_categorizer.py
-----------------
ML-based expense categorization using K-Means clustering.

When the Prolog engine returns "Other", we attempt to cluster the transaction
with similar past transactions using TF-IDF vectorization + K-Means.

This demonstrates the ML pipeline taught in the course:
  Text → TF-IDF Features → K-Means Clustering → Label Assignment
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize


class MLCategorizer:
    """
    Unsupervised ML categorizer using K-Means clustering on TF-IDF features.

    Pipeline:
        raw descriptions → TfidfVectorizer → normalized features → KMeans
    """

    def __init__(self, n_clusters: int = 6):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",   # character n-grams — handles typos & short strings
            ngram_range=(2, 4),
            max_features=500,
        )
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_labels: dict[int, str] = {}
        self.is_fitted = False

    def fit(self, descriptions: list[str], known_categories: list[str]):
        """
        Fit the model on transactions already labelled by the Prolog engine.
        Uses majority vote per cluster to assign human-readable labels.
        """
        if len(descriptions) < self.n_clusters:
            return  # not enough data

        X = self.vectorizer.fit_transform(descriptions)
        X = normalize(X)
        self.model.fit(X)

        # Assign a readable label to each cluster via majority vote
        cluster_assignments = self.model.labels_
        from collections import Counter
        for cluster_id in range(self.n_clusters):
            cats_in_cluster = [
                known_categories[i]
                for i, c in enumerate(cluster_assignments)
                if c == cluster_id and known_categories[i] != "Other"
            ]
            if cats_in_cluster:
                self.cluster_labels[cluster_id] = Counter(cats_in_cluster).most_common(1)[0][0]
            else:
                self.cluster_labels[cluster_id] = "Other"

        self.is_fitted = True

    def predict(self, description: str) -> str:
        """Predict category for a single new description."""
        if not self.is_fitted:
            return "Other"
        X = self.vectorizer.transform([description])
        X = normalize(X)
        cluster_id = self.model.predict(X)[0]
        return self.cluster_labels.get(cluster_id, "Other")

    def cluster_summary(self, descriptions: list[str], categories: list[str]) -> dict:
        """Returns per-cluster stats for display."""
        if not self.is_fitted:
            return {}
        X = self.vectorizer.transform(descriptions)
        X = normalize(X)
        assignments = self.model.predict(X)
        from collections import defaultdict
        summary = defaultdict(list)
        for desc, cat, cluster in zip(descriptions, categories, assignments):
            summary[self.cluster_labels.get(cluster, "Other")].append(desc)
        return dict(summary)
