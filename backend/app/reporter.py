# reporter.py
import json
from datetime import datetime

def make_report(claim: dict, judge_result: dict) -> dict:
    out = {
        "claim_id": claim.get("claim_id"),
        "customer_name": claim.get("customer_name"),
        "policy_number": claim.get("policy_number"),
        "incident_date": claim.get("incident_date"),
        "estimated_cost": claim.get("estimated_cost"),
        "damage": claim.get("damage"),
        "decision": judge_result.get("decision"),
        "confidence": judge_result.get("confidence"),
        "violated_rules": judge_result.get("violated_rules"),
        "rationale": judge_result.get("rationale"),
        "recommendation": judge_result.get("recommendation"),
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    return out

def report_to_markdown(report: dict) -> str:
    md = f"# Claim Report — {report['claim_id']}\n\n"
    md += f"- **Customer**: {report.get('customer_name')}\n"
    md += f"- **Policy**: {report.get('policy_number')}\n"
    md += f"- **Incident Date**: {report.get('incident_date')}\n"
    md += f"- **Estimated Cost**: {report.get('estimated_cost')}\n"
    md += f"- **Decision**: **{report.get('decision')}** (confidence {report.get('confidence')})\n\n"
    md += f"**Rationale:**\n\n{report.get('rationale')}\n\n"
    if report.get('violated_rules'):
        md += "Violated rules:\n\n"
        for r in report['violated_rules']:
            md += f"- {r}\n"
    if report.get('recommendation'):
        md += f"\n**Recommendation:** {report.get('recommendation')}\n"
    md += f"\n_Generated at {report.get('generated_at')}_\n"
    return md
