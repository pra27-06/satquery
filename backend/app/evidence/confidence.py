"""Evidence quality reporting for the MVP.

This module deliberately does not present heuristic agreement as a calibrated
probability. It reports the evidence status and the actual signals available
from the deterministic tools.
"""

from typing import Dict, Any

def compute_confidence(task: str, tool_results: Dict[str, Any], image_count: int) -> Dict[str, Any]:
    insufficient = bool(tool_results.get("insufficient_evidence", False))
    if insufficient:
        return {
            "confidence_score": None,
            "confidence_percentage": None,
            "rating": "INSUFFICIENT EVIDENCE",
            "calculation_basis": "The requested target is obscured or the available input is insufficient for reliable confirmation.",
            "mathematical_formula": None,
            "audit_metrics": {},
            "provenance_audit": [{
                "factor": "Evidence availability",
                "weight": "N/A",
                "value": "Insufficient",
                "positive": False,
                "scientific_rationale": "The MVP refuses to convert insufficient visual evidence into a numeric confidence probability."
            }]
        }

    factors = [{
        "factor": "Deterministic analysis completed",
        "weight": "N/A",
        "value": task,
        "positive": True,
        "scientific_rationale": "The result is produced by the selected deterministic computer-vision tool."
    }]
    if image_count == 2:
        factors.append({
            "factor": "Paired images supplied",
            "weight": "N/A",
            "value": "2 images",
            "positive": True,
            "scientific_rationale": "A two-image comparison can produce a pixel-level difference mask; geographic co-registration is not verified for ordinary image uploads."
        })

    return {
        "confidence_score": None,
        "confidence_percentage": None,
        "rating": "ANALYSIS COMPLETE — HEURISTIC",
        "calculation_basis": "No calibrated probability is claimed. Use the visual evidence, algorithm label, and input limitations shown in the report.",
        "mathematical_formula": None,
        "audit_metrics": {},
        "provenance_audit": factors
    }
