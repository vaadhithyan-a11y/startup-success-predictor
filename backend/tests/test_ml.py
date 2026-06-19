import pandas as pd
import numpy as np
from app.ml.data_ingestion import generate_synthetic_data
from app.ml.feature_engineering import FeatureEngineer


class TestDataIngestion:
    def test_generate_synthetic_data(self):
        df = generate_synthetic_data(n_samples=100)
        assert len(df) == 100
        assert "success_label" in df.columns
        assert "revenue_growth" in df.columns
        assert "industry" in df.columns
        assert df["success_label"].isin([0, 1]).all()

    def test_generate_synthetic_data_zero(self):
        df = generate_synthetic_data(n_samples=0)
        assert len(df) == 0


class TestFeatureEngineering:
    def test_feature_engineer_fit_transform(self):
        df = generate_synthetic_data(n_samples=200)
        feature_cols = [
            "industry", "revenue", "funding_raised", "employees",
            "burn_rate", "market_size", "growth_rate", "founder_experience",
        ]
        X = df[feature_cols]

        fe = FeatureEngineer()
        fe.fit(X)
        transformed = fe.transform(X)

        assert transformed.shape[0] == 200
        assert transformed.shape[1] > 0
        assert not np.any(np.isnan(transformed))

    def test_feature_engineer_derived(self):
        df = pd.DataFrame({
            "industry": ["Tech"],
            "revenue": [1_000_000],
            "funding_raised": [5_000_000],
            "employees": [50],
            "burn_rate": [100_000],
            "market_size": [500_000_000],
            "growth_rate": [0.5],
            "founder_experience": [10],
        })
        fe = FeatureEngineer()
        fe.fit(df)
        transformed = fe.transform(df)
        assert transformed.shape[0] == 1


class TestModelTraining:
    def test_train_success_model(self):
        from app.ml.model_training import train_success_model
        df = generate_synthetic_data(n_samples=200)
        result = train_success_model(df, model_type="random_forest")
        assert "roc_auc" in result
        assert "accuracy" in result
        assert "model_path" in result
        assert result["roc_auc"] > 0.5

    def test_train_growth_model(self):
        from app.ml.model_training import train_growth_model
        df = generate_synthetic_data(n_samples=200)
        result = train_growth_model(df, model_type="random_forest")
        assert "mae" in result
        assert "r2" in result
        assert "model_path" in result
