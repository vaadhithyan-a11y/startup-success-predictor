import numpy as np
from app.ml.data_ingestion import generate_synthetic_data
from app.services.prediction_service import PredictionService


class DashboardService:
    def __init__(self):
        self._prediction_service = PredictionService()

    def get_dashboard_data(self) -> dict:
        data = generate_synthetic_data(n_samples=100)

        rankings = []
        for i, row in data.iterrows():
            prob = self._prediction_service.predict_success(
                row["industry"], row["revenue"], row["employees"],
                row["founder_experience"], row["funding_raised"],
                row["market_size"], row["growth_rate"],
            )
            rankings.append({
                "name": f"Startup {i + 1}",
                "score": prob["success_probability"],
                "industry": row["industry"],
            })
        rankings.sort(key=lambda x: x["score"], reverse=True)

        risk_distribution = {
            "Low (0-30)": 0,
            "Medium (30-60)": 0,
            "High (60-100)": 0,
        }
        for _, row in data.iterrows():
            burn_rate = row.get("burn_rate", 0)
            risk_score = min(max(burn_rate / 10000, 0), 100)
            if risk_score < 30:
                risk_distribution["Low (0-30)"] += 1
            elif risk_score < 60:
                risk_distribution["Medium (30-60)"] += 1
            else:
                risk_distribution["High (60-100)"] += 1

        funding_trends = [
            {"year": 2020 + i, "amount": float(np.random.uniform(5e8, 5e9))}
            for i in range(5)
        ]

        industry_analysis = {}
        for ind in data["industry"].unique():
            subset = data[data["industry"] == ind]
            avg_success = subset["growth_rate"].mean() * 100
            industry_analysis[ind] = {
                "count": int(len(subset)),
                "avg_success": round(float(avg_success), 1),
            }

        return {
            "rankings": rankings[:10],
            "risk_distribution": risk_distribution,
            "funding_trends": funding_trends,
            "industry_analysis": industry_analysis,
        }
