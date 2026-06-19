import pandas as pd
import numpy as np


def generate_synthetic_data(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    industries = ["Tech", "Healthcare", "Fintech", "E-commerce", "AI/ML", "CleanTech"]

    data = {
        "industry": np.random.choice(industries, n_samples),
        "revenue": np.random.exponential(scale=5_000_000, size=n_samples),
        "funding_raised": np.random.exponential(scale=10_000_000, size=n_samples),
        "employees": np.random.randint(1, 1000, n_samples),
        "burn_rate": np.random.exponential(scale=500_000, size=n_samples),
        "market_size": np.random.exponential(scale=1_000_000_000, size=n_samples),
        "growth_rate": np.random.uniform(-0.2, 1.5, n_samples),
        "founder_experience": np.random.uniform(0, 30, n_samples),
    }
    df = pd.DataFrame(data)

    revenue_per_employee = np.where(df["employees"] > 0, df["revenue"] / df["employees"], 0)
    burn_multiple = np.where(df["revenue"] > 0, df["burn_rate"] / df["revenue"], 0)
    funding_efficiency = np.where(df["funding_raised"] > 0, df["revenue"] / df["funding_raised"], 0)

    success_score = (
        0.3 * np.log1p(df["revenue"]) / 15
        + 0.2 * np.log1p(df["market_size"]) / 20
        + 0.15 * df["growth_rate"]
        + 0.1 * np.log1p(funding_efficiency + 1) / 5
        + 0.1 * df["founder_experience"] / 30
        - 0.1 * np.log1p(burn_multiple + 1) / 3
        + 0.05 * np.log1p(revenue_per_employee + 1) / 10
        + np.random.normal(0, 0.15, n_samples)
    )
    df["success_label"] = (success_score > success_score.median()).astype(int)
    df["revenue_growth"] = df["growth_rate"] + np.random.normal(0, 0.1, n_samples)

    return df


def load_csv(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)


def load_excel(filepath: str) -> pd.DataFrame:
    return pd.read_excel(filepath)
