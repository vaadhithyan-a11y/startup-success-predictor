import os
import joblib
from typing import Optional

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def load_model(model_name: str) -> Optional[object]:
    path = os.path.join(MODELS_DIR, model_name)
    if not os.path.exists(path):
        return None
    return joblib.load(path)


def get_success_model_path() -> str:
    path = os.path.join(MODELS_DIR, "success_random_forest.joblib")
    if os.path.exists(path):
        return path
    return ""


def get_growth_model_path() -> str:
    path = os.path.join(MODELS_DIR, "growth_random_forest.joblib")
    if os.path.exists(path):
        return path
    return ""
