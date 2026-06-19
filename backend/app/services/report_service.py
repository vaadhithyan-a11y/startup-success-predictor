import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from app.services.prediction_service import PredictionService

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

prediction_service = PredictionService()


def _build_summary_from_predictions(startup_name: str, industry: str,
                                    success: dict, growth: dict, risk: dict) -> dict:
    strengths = []
    weaknesses = []

    if success.get("success_probability", 0) > 60:
        strengths.append("High success probability score")
    else:
        weaknesses.append("Below-average success probability")

    if risk.get("financial_risk", 50) < 30:
        strengths.append("Strong financial position")
    elif risk.get("financial_risk", 50) > 70:
        weaknesses.append("High financial risk exposure")

    if risk.get("market_risk", 50) < 30:
        strengths.append("Favorable market conditions")
    elif risk.get("market_risk", 50) > 70:
        weaknesses.append("Challenging market environment")

    if growth.get("growth_1y", 0) > 0:
        strengths.append("Positive revenue growth trajectory")
    else:
        weaknesses.append("Revenue growth concerns")

    if not strengths:
        strengths = ["Established business operations"]
    if not weaknesses:
        weaknesses = ["Limited identifiable weaknesses"]

    return {
        "executive_summary": (
            f"{startup_name} operates in the {industry} sector with a "
            f"success probability of {success.get('success_probability', 0):.1f}%. "
            f"The venture shows a risk score of {risk.get('risk_score', 50):.1f} "
            f"with projected 1-year revenue growth of ${growth.get('growth_1y', 0):,.0f}."
        ),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "risk_analysis": {
            "financial": risk.get("financial_risk", 50),
            "operational": risk.get("operational_risk", 50),
            "market": risk.get("market_risk", 50),
            "team": risk.get("team_risk", 50),
        },
        "growth_potential": {
            "year_1": growth.get("growth_1y", 0),
            "year_3": growth.get("growth_3y", 0),
            "year_5": growth.get("growth_5y", 0),
        },
        "recommendation": (
            "Strong Buy" if success.get("success_probability", 0) > 70
            else "Buy" if success.get("success_probability", 0) > 50
            else "Hold" if success.get("success_probability", 0) > 30
            else "Sell"
        ),
    }


def _generate_pdf(startup_name: str, summary: dict) -> str:
    filename = f"report_{startup_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=24, spaceAfter=12)
    heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading1"], fontSize=16, spaceAfter=8, textColor=HexColor("#1a56db"))
    body_style = ParagraphStyle("CustomBody", parent=styles["Normal"], fontSize=11, spaceAfter=6, leading=14)

    elements = []
    elements.append(Paragraph(f"Investment Report: {startup_name}", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style))
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(Paragraph(summary["executive_summary"], body_style))
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Strengths", heading_style))
    for s in summary["strengths"]:
        elements.append(Paragraph(f"• {s}", body_style))
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Weaknesses", heading_style))
    for w in summary["weaknesses"]:
        elements.append(Paragraph(f"• {w}", body_style))
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Risk Analysis", heading_style))
    risk_data = [["Category", "Score (0-100)"]]
    for category, score in summary["risk_analysis"].items():
        risk_data.append([category.capitalize(), str(score)])
    risk_table = Table(risk_data, colWidths=[2.5 * inch, 1.5 * inch])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a56db")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#f3f4f6")),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Growth Potential", heading_style))
    growth_data = [["Period", "Projected Revenue"]]
    for period, value in summary["growth_potential"].items():
        growth_data.append([period.replace("_", " ").capitalize(), f"${value:,.0f}"])
    growth_table = Table(growth_data, colWidths=[2.5 * inch, 2.5 * inch])
    growth_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a56db")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#f3f4f6")),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(growth_table)
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph(f"Recommendation: {summary['recommendation']}", heading_style))

    doc.build(elements)
    return filepath


class ReportService:
    def __init__(self):
        self.prediction_service = prediction_service

    def generate_report(self, startup_name: str, industry: str,
                        revenue: float, employees: int,
                        founder_experience: float, funding_raised: float,
                        market_size: float, growth_rate: float,
                        burn_rate: float, customer_growth: float) -> dict:
        success = self.prediction_service.predict_success(
            industry, revenue, employees, founder_experience,
            funding_raised, market_size, customer_growth,
        )
        growth = self.prediction_service.predict_growth(
            revenue, employees, funding_raised, market_size, growth_rate,
        )
        risk = self.prediction_service.predict_risk(
            industry, revenue, employees, founder_experience,
            funding_raised, market_size, growth_rate, burn_rate,
        )

        summary = _build_summary_from_predictions(startup_name, industry, success, growth, risk)
        pdf_path = _generate_pdf(startup_name, summary)

        return {
            "report_id": hash(pdf_path) % 1000000,
            "pdf_url": f"/reports/{os.path.basename(pdf_path)}",
            "summary": summary,
        }
