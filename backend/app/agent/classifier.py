"""
classifier.py
-------------
Agentic query understanding and sensor-aware task router.
Analyzes natural language queries alongside detected satellite raster
modalities (Optical vs SAR) to select optimal tools and identify
missing data modalities.
"""

from typing import Dict, Any, List, Optional

def classify_query(
    query: str,
    image_count: int,
    detected_modalities: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Classifies the user query and image inputs into an agentic task plan.
    Incorporates image modality detections to automatically route
    to Optical-SAR Fusion or single-image SAR/Optical VQA.
    """
    q = query.strip().lower()
    modalities = [m.get("modality", "OPTICAL_RGB") for m in (detected_modalities or [])]
    has_sar = any(m == "SAR_RADAR" for m in modalities)
    has_optical = any(m == "OPTICAL_RGB" for m in modalities)
    
    missing_requirement = None
    
    # 1. Optical + SAR Cross-Modal Fusion
    # Trigger if explicitly requested, or if 2 images uploaded where 1 is SAR and 1 is Optical!
    if (image_count == 2 and (has_sar and has_optical)) or (image_count == 2 and ("optical" in q or "sar" in q or "radar" in q or "fusion" in q)):
        task = "OPTICAL_SAR_FUSION"
        target = "water_and_builtup"
        description = "Co-registered Optical and SAR Fusion Analysis"
        tool_name = "optical_sar_fusion_tool"
        expected_images = 2
        
    elif image_count == 1 and ("fusion" in q or ("optical" in q and "sar" in q)):
        # User wants fusion but uploaded only 1 image!
        # Fall back to single VQA and flag missing modality
        task = "SINGLE_VQA"
        target = "land_cover"
        description = "Single-Image Analysis (Awaiting Companion Image for Fusion)"
        tool_name = "single_vqa_tool"
        expected_images = 1
        missing_requirement = {
            "needed": "OPTICAL_RGB" if has_sar else "SAR_RADAR",
            "message": "You requested Optical+SAR Fusion, but only 1 image was uploaded. Please upload the companion sensor image."
        }
        
    # 2. Bi-Temporal Change Analysis & Change VQA
    elif any(k in q for k in ["change", "dates", "difference", "increased", "decreased", "between", "expansion", "before and after"]):
        if image_count >= 2:
            if any(k in q for k in ["increase", "decrease", "has the", "how much", "percentage", "rate"]):
                task = "CHANGE_VQA"
                target = "built_up_change"
                description = "Bi-Temporal Quantitative Change Visual Question Answering"
                tool_name = "change_vqa_tool"
            else:
                task = "TEMPORAL_CHANGE"
                target = "spatial_difference"
                description = "Bi-Temporal Spatial Change Detection & Heatmap Mapping"
                tool_name = "change_detection_tool"
            expected_images = 2
        else:
            # User asked about change but only uploaded 1 image!
            task = "SINGLE_VQA"
            target = "land_cover"
            description = "Single-Image Baseline Assessment (Second Temporal Timestamp Needed)"
            tool_name = "single_vqa_tool"
            expected_images = 1
            missing_requirement = {
                "needed": "TEMPORAL_T2",
                "message": "Change detection requires two timestamps (Before and After). Showing baseline analysis for this scene; please upload the second image."
            }
            
    # 3. Text-guided Visual Grounding
    elif any(k in q for k in ["highlight", "locate", "ground", "find", "bounding box", "detect", "point out", "segment"]):
        task = "GROUNDING"
        if "water" in q or "lake" in q or "river" in q or "ocean" in q or "pond" in q:
            target = "water"
        elif "runway" in q or "airport" in q or "flight" in q or "tarmac" in q:
            target = "runway"
        elif "urban" in q or "building" in q or "structure" in q or "settlement" in q:
            target = "building"
        elif "crop" in q or "farm" in q or "field" in q:
            target = "agriculture"
        else:
            target = "general_objects"
        description = f"Text-Guided Spatial Grounding ({target})"
        tool_name = "grounding_tool"
        expected_images = 1
        
    # 4. Default: Single-Image VQA & Scene Understanding
    else:
        if image_count == 2:
            # If 2 images uploaded with generic question, default to temporal change
            task = "TEMPORAL_CHANGE"
            target = "spatial_difference"
            description = "Bi-Temporal Spatial Change Detection & Heatmap Mapping"
            tool_name = "change_detection_tool"
            expected_images = 2
        else:
            task = "SINGLE_VQA"
            target = "land_cover"
            description = "Single-Image Remote Sensing Visual Question Answering & Land-Cover Assessment"
            tool_name = "single_vqa_tool"
            expected_images = 1
            
    return {
        "task": task,
        "target": target,
        "description": description,
        "tool_name": tool_name,
        "expected_images": expected_images,
        "missing_requirement": missing_requirement,
        "has_sar": has_sar,
        "has_optical": has_optical,
        "confidence_prior": 0.94
    }
