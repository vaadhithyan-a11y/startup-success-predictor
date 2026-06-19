import os
import joblib
import pandas as pd

from app.ml.model_loader import get_success_model_path, get_growth_model_path


MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")


def _rule_based_success_probability(industry: str, revenue: float, employees: int,
                                    founder_experience: float, funding_raised: float,
                                    market_size: float, customer_growth: float) -> float:
    score = 0.0
    score += min(revenue / 10_000_000, 1.0) * 0.25
    score += min(market_size / 1_000_000_000, 1.0) * 0.20
    score += min(customer_growth, 1.0) * 0.15
    score += min(founder_experience / 20, 1.0) * 0.15
    score += min(funding_raised / 20_000_000, 1.0) * 0.10
    score += min(employees / 500, 1.0) * 0.10
    industry_bonus = {"Tech": 0.05, "AI/ML": 0.10, "Healthcare": 0.05, "Fintech": 0.05}
    score += industry_bonus.get(industry, 0)
    return min(max(score, 0.0), 1.0) * 100


def _rule_based_growth_forecast(revenue: float, employees: int,
                                funding_raised: float, market_size: float,
                                growth_rate: float) -> tuple:
    base_growth = growth_rate * revenue
    growth_1y = revenue * (1 + base_growth / revenue) if revenue > 0 else base_growth
    growth_3y = revenue * (1 + base_growth / revenue) ** 3 if revenue > 0 else base_growth * 3
    growth_5y = revenue * (1 + base_growth / revenue) ** 5 if revenue > 0 else base_growth * 5
    return float(growth_1y), float(growth_3y), float(growth_5y)


def _rule_based_risk_scores(industry: str, revenue: float, employees: int,
                            founder_experience: float, funding_raised: float,
                            market_size: float, growth_rate: float,
                            burn_rate: float) -> dict:
    financial_risk = min(max((burn_rate / (revenue + 1)) * 50, 10), 90)
    operational_risk = min(max((1 - employees / 1000) * 80, 10), 90)
    market_risk = min(max((1 - market_size / 2_000_000_000) * 80, 10), 90)
    team_risk = min(max((1 - founder_experience / 25) * 80, 10), 90)
    risk_score = (financial_risk + operational_risk + market_risk + team_risk) / 4
    return {
        "financial_risk": round(financial_risk, 2),
        "operational_risk": round(operational_risk, 2),
        "market_risk": round(market_risk, 2),
        "team_risk": round(team_risk, 2),
        "risk_score": round(risk_score, 2),
    }


class PredictionService:
    def __init__(self):
        self.success_model = None
        self.growth_model = None
        self._load_models()

    def _load_models(self):
        success_path = get_success_model_path()
        growth_path = get_growth_model_path()
        if success_path:
            self.success_model = joblib.load(success_path)
        if growth_path:
            self.growth_model = joblib.load(growth_path)

    def predict_success(self, industry: str, revenue: float, employees: int,
                        founder_experience: float, funding_raised: float,
                        market_size: float, customer_growth: float) -> dict:
        if self.success_model:
            df = pd.DataFrame([{
                "industry": industry, "revenue": revenue, "funding_raised": funding_raised,
                "employees": employees, "burn_rate": 0, "market_size": market_size,
                "growth_rate": customer_growth, "founder_experience": founder_experience,
            }])
            proba = self.success_model.predict_proba(df)[:, 1][0] * 100
            return {"success_probability": round(float(proba), 2), "model_version": "ml_v1"}
        proba = _rule_based_success_probability(
            industry, revenue, employees, founder_experience,
            funding_raised, market_size, customer_growth,
        )
        return {"success_probability": round(proba, 2), "model_version": "rule_based"}

    def predict_growth(self, revenue: float, employees: int,
                       funding_raised: float, market_size: float,
                       growth_rate: float) -> dict:
        if self.growth_model:
            df = pd.DataFrame([{
                "revenue": revenue, "employees": employees,
                "funding_raised": funding_raised, "market_size": market_size,
                "growth_rate": growth_rate,
            }])
            preds = self.growth_model.predict(df)
            return {
                "growth_1y": round(float(preds[0] * revenue), 2),
                "growth_3y": round(float(preds[0] * revenue * 3), 2),
                "growth_5y": round(float(preds[0] * revenue * 5), 2),
                "model_version": "ml_v1",
            }
        g1, g3, g5 = _rule_based_growth_forecast(
            revenue, employees, funding_raised, market_size, growth_rate,
        )
        return {"growth_1y": round(g1, 2), "growth_3y": round(g3, 2), "growth_5y": round(g5, 2), "model_version": "rule_based"}

    def predict_risk(self, industry: str, revenue: float, employees: int,
                     founder_experience: float, funding_raised: float,
                     market_size: float, growth_rate: float,
                     burn_rate: float) -> dict:
        return _rule_based_risk_scores(
            industry, revenue, employees, founder_experience,
            funding_raised, market_size, growth_rate, burn_rate,
        )
