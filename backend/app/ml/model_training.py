import pandas as pd
import joblib
import os
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.ml.feature_engineering import FeatureEngineer


MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def train_success_model(df: pd.DataFrame, model_type: str = "random_forest") -> dict:
    feature_cols = [
        "industry", "revenue", "funding_raised", "employees",
        "burn_rate", "market_size", "growth_rate", "founder_experience",
    ]
    X = df[feature_cols]
    y = df["success_label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    fe = FeatureEngineer()
    if model_type == "xgboost":
        model = xgb.XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, eval_metric="logloss",
        )
    else:
        model = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_leaf=5,
            random_state=42,
        )

    pipeline = Pipeline([
        ("features", fe),
        ("classifier", model),
    ])
    pipeline.fit(X_train, y_train)

    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    y_pred = pipeline.predict(X_test)
    accuracy = (y_pred == y_test).mean()

    model_path = os.path.join(MODELS_DIR, f"success_{model_type}.joblib")
    joblib.dump(pipeline, model_path)

    return {
        "model_type": model_type,
        "roc_auc": float(auc),
        "accuracy": float(accuracy),
        "model_path": model_path,
        "model_version": f"{model_type}_v1",
    }


def train_growth_model(df: pd.DataFrame, model_type: str = "linear_regression") -> dict:
    feature_cols = [
        "revenue", "employees", "funding_raised", "market_size", "growth_rate",
    ]
    X = df[feature_cols]
    y = df["revenue_growth"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if model_type == "xgboost":
        model = xgb.XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42,
        )
    else:
        model = RandomForestRegressor(
            n_estimators=100, max_depth=10, min_samples_leaf=5,
            random_state=42,
        )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", model),
    ])
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    model_path = os.path.join(MODELS_DIR, f"growth_{model_type}.joblib")
    joblib.dump(pipeline, model_path)

    return {
        "model_type": model_type,
        "mae": float(mae),
        "r2": float(r2),
        "model_path": model_path,
        "model_version": f"growth_{model_type}_v1",
    }
