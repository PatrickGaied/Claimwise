# cleaner.py
import uuid  # For generating unique claim IDs

def normalize_claim(parsed: dict) -> dict:
    """
    Merge heuristics and LLM outputs; assign claim_id if missing.
    Clean up and standardize the extracted claim data.
    """
    out = parsed.copy()
    
    # Generate a unique claim ID if missing
    if not out.get("claim_id"):
        out["claim_id"] = str(uuid.uuid4())[:8]  # Short 8-character ID
    
    # normalize cost to number
    if out.get("estimated_cost") is not None:
        try:
            out["estimated_cost"] = float(out["estimated_cost"])
        except:
            pass
    
    # trim whitespace from text fields
    for k in ["damage", "customer_name", "policy_number"]:
        if out.get(k) and isinstance(out[k], str):
            out[k] = out[k].strip()
    
    # preserve any conflicts found during extraction
    out.setdefault("source_conflicts", out.get("conflicts", []))
    return out
