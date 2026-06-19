import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder


class FeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.column_transformer = None
        self.numeric_features = [
            "revenue", "funding_raised", "employees", "burn_rate",
            "market_size", "growth_rate", "founder_experience",
        ]
        self.categorical_features = ["industry"]
        self.derived_features = [
            "revenue_per_employee", "burn_multiple", "funding_efficiency",
        ]

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["revenue_per_employee"] = np.where(
            df["employees"] > 0, df["revenue"] / df["employees"], 0
        )
        df["burn_multiple"] = np.where(
            df["revenue"] > 0, df["burn_rate"] / df["revenue"], 0
        )
        df["funding_efficiency"] = np.where(
            df["funding_raised"] > 0, df["revenue"] / df["funding_raised"], 0
        )
        return df

    def fit(self, X: pd.DataFrame, y=None):
        X_feat = self._add_derived_features(X)
        all_numeric = self.numeric_features + self.derived_features
        available_numeric = [f for f in all_numeric if f in X_feat.columns]
        available_cat = [f for f in self.categorical_features if f in X_feat.columns]

        transformers = []
        if available_numeric:
            transformers.append(("num", StandardScaler(), available_numeric))
        if available_cat:
            transformers.append(("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), available_cat))

        self.column_transformer = ColumnTransformer(transformers, remainder="drop")
        self.column_transformer.fit(X_feat)
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        X_feat = self._add_derived_features(X)
        return self.column_transformer.transform(X_feat)

    def get_feature_names(self):
        return self.column_transformer.get_feature_names_out()
