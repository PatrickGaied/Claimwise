# judge.py
import json
from .llm_client import call_llm
import datetime
import os
from pathlib import Path

RULEBOOK = {
    "policy_active": "Policy must be active at incident date.",
    "within_limits": "Estimated cost must be less than or equal to policy coverage.",
    "covered_incident": "Incident type must be one of covered categories: accident, theft, fire, natural disaster.",
    "no_conflict": "Key fields must not have unresolved contradictions."
}

# deterministic policy check using sample_policies.json
def load_policies():
    here = Path(__file__).parent
    p = here / "sample_policies.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}

POLICIES = load_policies()

def deterministic_checks(claim: dict) -> dict:
    results = {"violations": [], "notes": []}
    pol = POLICIES.get(claim.get("policy_number"))
    if not pol:
        results["notes"].append("Policy number not found in local DB; cannot deterministically validate.")
    else:
        # check active
        incident = claim.get("incident_date")
        if incident:
            try:
                inc_date = datetime.date.fromisoformat(incident)
                start = datetime.date.fromisoformat(pol["start_date"])
                end = datetime.date.fromisoformat(pol["end_date"])
                if not (start <= inc_date <= end):
                    results["violations"].append("policy_active")
            except Exception:
                results["notes"].append("Could not parse incident date for policy check.")
        # coverage
        cov = pol.get("coverage_limit")
        ec = claim.get("estimated_cost")
        if cov is not None and ec is not None:
            if ec > cov:
                results["violations"].append("within_limits")
    return results

# LLM judge: apply the rulebook and output decision + rationale
JUDGE_PROMPT = """
You are an expert insurance claims adjuster with 15+ years of experience. Apply this RULEBOOK:
{rulebook}

Given this claim (JSON):
{claim_json}

Analyze this claim thoroughly and provide a detailed assessment. Consider:
- Policy coverage limits and exclusions
- Risk factors and red flags
- Documentation completeness
- Cost reasonableness for damage type
- Timeline consistency
- Fraud indicators

Return a JSON with:
{{
  "decision": "Approve" | "Deny" | "Review",
  "confidence": 0.0-1.0,
  "violated_rules": [ ... ],
  "rationale": "Provide a detailed, specific analysis (4-6 sentences) explaining your reasoning, citing specific claim details, policy provisions, and industry standards. Vary your language and focus on unique aspects of this particular claim.",
  "recommendation": "If Review, what specific documentation or investigation steps are needed"
}}

Make your rationale unique and specific to this claim. Avoid generic language. Reference actual dollar amounts, dates, policy numbers, and damage types from the claim data.
Only output JSON.
"""

def llm_judge(claim: dict) -> dict:
    prompt = JUDGE_PROMPT.format(rulebook=json.dumps(RULEBOOK, indent=2), claim_json=json.dumps(claim, indent=2))
    resp = call_llm(prompt, max_tokens=500, temperature=0.0)
    txt = resp.get("text", "")
    import re
    try:
        cleaned = re.sub(r"^```json\s*|```$", "", txt.strip())
        return json.loads(cleaned)
    except Exception:
        # fallback simple rule. could be more comprehensive.
        det = deterministic_checks(claim)
        if det["violations"]:
            return {"decision": "Deny", "confidence": 0.75, "violated_rules": det["violations"], "rationale": "Deterministic policy violations found.", "recommendation": "Request policy documents / proof of incident."}
        return {"decision": "Review", "confidence": 0.6, "violated_rules": [], "rationale": "Insufficient deterministic evidence — please review.", "recommendation": "Ask for photos, police report, or policy docs."}
