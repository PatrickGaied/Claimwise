# parser.py
import re
import json
from dateutil.parser import parse as dateparse
from .llm_client import call_llm

# Basic regex extractors
AMOUNT_RE = re.compile(r"\$?\s?([0-9]{1,3}(?:[,0-9]*)(?:\.[0-9]{2})?)")
DATE_CANDIDATE = re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2})")
POLICY_RE = re.compile(r"(policy\s*(?:#|no\.?|number)[:\s]*([A-Z0-9\-]+))", re.I)
NAME_RE = re.compile(r"(?:Name[:\s]*)([A-Z][a-z]+\s+[A-Z][a-z]+)")

def first_match(re_obj, text):
    m = re_obj.search(text)
    return m.group(1) if m else None

def try_parse_date(text):
    try:
        dt = dateparse(text, fuzzy=True)
        return dt.date().isoformat()
    except Exception:
        return None

def extract_fields_simple(text: str) -> dict:
    # heuristics
    claim = {}
    claim['raw_text'] = text[:6000]
    m_amount = AMOUNT_RE.search(text)
    if m_amount:
        claim['estimated_cost'] = float(m_amount.group(1).replace(',', ''))
    # dates
    d = DATE_CANDIDATE.search(text)
    if d:
        parsed = try_parse_date(d.group(1))
        claim['incident_date'] = parsed
    # policy
    p = POLICY_RE.search(text)
    if p:
        claim['policy_number'] = p.group(2)
    # name
    n = NAME_RE.search(text)
    if n:
        claim['customer_name'] = n.group(1)
    return claim

# LLM fallback to extract structured JSON
EXTRACTION_PROMPT = """You are a senior insurance claims analyst with expertise in document processing.
Input: {raw_text}

Task: Carefully analyze this claim document and extract key information. Pay attention to:
- Specific damage descriptions and causes
- Exact monetary amounts and cost breakdowns
- Precise dates and timelines
- Policy details and coverage types
- Claimant information and contact details
- Any inconsistencies or missing information

Extract the following fields as strict JSON (no commentary) in this structure:
{{
  "claim_id": "<short id or null>",
  "customer_name": "<Full name or null>",
  "policy_number": "<policy id or null>",
  "incident_date": "<YYYY-MM-DD or null>",
  "damage": "<detailed, specific description of damage and cause - be descriptive and unique>",
  "estimated_cost": <number or null>,
  "sources": ["specific text snippets that support your extraction", ...],
  "conflicts": ["detailed explanation of any inconsistencies, missing info, or red flags you notice"]
}}

Be thorough and specific in your damage descriptions. Avoid generic terms like "property damage" - instead describe what specifically was damaged and how.
Only output JSON.
"""

def extract_with_llm(text: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(raw_text=text[:4000])
    resp = call_llm(prompt, max_tokens=600, temperature=0.0)
    raw = resp.get("text", "").strip()
    # attempt to safely parse JSON in response (robust)
    try:
        # sometimes LLM returns text with surrounding backticks or code fences
        import re
        code = re.sub(r"^```json\s*|```$|^```", "", raw.strip())
        return json.loads(code)
    except Exception as e:
        # fallback: return simple heuristics
        return extract_fields_simple(text)
