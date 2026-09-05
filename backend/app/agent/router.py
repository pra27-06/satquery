"""
router.py
---------
Agentic Router: Central orchestrator connecting input validation,
query classification, tool execution, and evidence compilation.
Equipped with automated sensor modality detection (SAR vs Optical)
and intelligent cross-modal guidance.
"""

import uuid
from typing import List, Dict, Any
import numpy as np

from .classifier import classify_query
from .trace import AgentTrace
from ..geospatial.validation import validate_inputs
from ..geospatial.modality_detector import detect_modality
from ..tools.vqa import run_single_vqa
from ..tools.grounding import run_grounding
from ..tools.change_detection import run_change_analysis
from ..tools.optical_sar import run_optical_sar_fusion
from ..evidence.confidence import compute_confidence
from ..evidence.report_generator import generate_evidence_report
from ..api.report import store_report

def execute_agent_pipeline(
    query: str,
    images: List[np.ndarray],
    metadata_list: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes the 5-stage agentic remote sensing pipeline with sensor awareness.
    """
    session_id = str(uuid.uuid4())
    trace = AgentTrace()
    trace.add_step("INGEST", f"Ingested {len(images)} raster stream(s) for query: '{query}'")
    
    # Stage 0: Sensor & Modality Detection
    modality_analyses = [detect_modality(img) for img in images]
    for idx, m in enumerate(modality_analyses):
        trace.add_step(
            "SENSOR_SCAN",
            f"Raster #{idx+1}: Diagnosed as {m['sensor_family']} (speckle index={m['speckle_index']})",
            {"subsystem": "Classical RS Diagnostic", "component": "Radiometric & Spatial Feature Extractor", "derivation": m.get("sensor_derivation")}
        )
    
    # Stage 1: Query & Sensor Classification
    plan = classify_query(query, len(images), detected_modalities=modality_analyses)
    trace.add_step(
        "INTENT_PLAN",
        f"Interpreted query intent: mapped to task '{plan['task']}' with target '{plan['target']}'. Selected execution tool: {plan['tool_name']}",
        {"subsystem": "AI Agent Reasoner", "component": "Semantic Intent Parser & Tool Planner", "expected_images": plan["expected_images"]}
    )
    
    # Stage 2: Input Validation
    validation = validate_inputs(images, plan["expected_images"], modality=plan["task"])
    trace.add_step(
        "VALIDATE",
        f"Verified {validation['image_count']} raster(s) @ {validation['dimensions']}, co-registration valid: {validation['co_registered']}",
        {"subsystem": "Geospatial Preflight", "component": "Affine Grid & Co-Registration Validator"}
    )
    
    # Stage 3: Tool Execution
    task = plan["task"]
    trace.add_step(
        "DISPATCH", 
        f"Dispatching payload to specialist tool '{plan['tool_name']}'",
        {"subsystem": "AI Agent Orchestrator", "component": "Deterministic Tool Dispatcher"}
    )
    
    if task == "SINGLE_VQA":
        tool_res = run_single_vqa(images[0], query)
    elif task == "GROUNDING":
        tool_res = run_grounding(images[0], plan["target"], query)
    elif task in ("TEMPORAL_CHANGE", "CHANGE_VQA"):
        tool_res = run_change_analysis(images[0], images[1], query, task=task)
    elif task == "OPTICAL_SAR_FUSION":
        # Ensure image 0 is optical and image 1 is SAR if mixed
        if len(images) == 2 and modality_analyses[0]["is_radar"] and not modality_analyses[1]["is_radar"]:
            opt_img, sar_img = images[1], images[0]
        else:
            opt_img, sar_img = images[0], images[1]
        tool_res = run_optical_sar_fusion(opt_img, sar_img, query)
    else:
        tool_res = run_single_vqa(images[0], query)
        
    trace.add_step(
        "COMPUTE", 
        f"Executed spatial algorithms in '{plan['tool_name']}'. Extracted physical indices and area statistics.",
        {"subsystem": "Classical RS/CV Engine", "component": "Deterministic Physical Algorithm Pipeline"}
    )
    
    # Stage 4: Dual-Estimate Confidence Scoring
    confidence = compute_confidence(task, tool_res, len(images))
    trace.add_step(
        "CONFIDENCE",
        f"Derived empirical confidence: {confidence['confidence_percentage']} ({confidence['rating']})",
        {"subsystem": "Uncertainty Engine", "component": "Multi-Factor Statistical Consensus Evaluator", "formula": confidence.get("mathematical_formula")}
    )
    
    # Stage 5: Evidence Compilation
    report = generate_evidence_report(
        session_id=session_id,
        query=query,
        classification=plan,
        validation_info=validation,
        tool_results=tool_res,
        confidence=confidence,
        trace_log=trace.get_trace_log()
    )
    trace.add_step(
        "REPORT", 
        f"Packaged verifiable evidence report: {report['data']['report_id']}",
        {"subsystem": "Evidence Synthesizer", "component": "Audit Report Generator"}
    )
    
    # Consolidate and strictly deduplicate guidance notes
    guidance_notes = []
    seen = set()
    if plan.get("missing_requirement"):
        msg = plan["missing_requirement"]["message"]
        if msg not in seen:
            guidance_notes.append(msg)
            seen.add(msg)
    if "guidance" in tool_res and isinstance(tool_res["guidance"], dict):
        if "missing_modality_alert" in tool_res["guidance"]:
            msg = tool_res["guidance"]["missing_modality_alert"]
            if msg not in seen:
                guidance_notes.append(msg)
                seen.add(msg)
    for m in modality_analyses:
        for rec in m.get("recommendations", []):
            if rec not in seen:
                guidance_notes.append(rec)
                seen.add(rec)
                
    # Store report for new tab viewing via /api/report/{session_id} or /api/report/{report_id}
    store_report(session_id, report["html"], report["data"])
    store_report(report["data"]["report_id"], report["html"], report["data"])
    
    return {
        "session_id": session_id,
        "query": query,
        "task": plan["task"],
        "task_description": plan["description"],
        "tool_used": plan["tool_name"],
        "modalities": modality_analyses,
        "guidance_notes": guidance_notes,
        "answer": tool_res.get("answer"),
        "confidence": confidence,
        "results": tool_res,
        "engineering_telemetry": tool_res.get("engineering_telemetry", {}),
        "trace": trace.get_trace_log(),
        "report_id": report["data"]["report_id"],
        "report_html": report["html"],
        "report_url": f"/api/report/{session_id}",
        "duration_ms": trace.total_duration_ms()
    }
