"""
analyze.py
----------
Primary analysis and sensor pre-scanning endpoints for SatQuery AI.
Accepts multipart imagery, performs rapid sensor diagnostics,
and executes the agentic remote sensing pipeline.
"""

from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from ..geospatial.raster_io import load_raster
from ..geospatial.modality_detector import detect_modality
from ..agent.router import execute_agent_pipeline

router = APIRouter()

@router.post("/prescan")
async def prescan_endpoint(
    files: List[UploadFile] = File(...)
):
    """
    Ultra-fast (<20ms) sensor and modality diagnostic pre-scan.
    Provides instant sensor identification, feature breakdown,
    and missing modality recommendations before running full execution.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one file must be uploaded for pre-scanning.")
        
    results = []
    has_sar = False
    has_optical = False
    
    for file in files:
        contents = await file.read()
        try:
            arr, meta = load_raster(contents)
            info = detect_modality(arr)
            info["filename"] = file.filename
            results.append(info)
            if info["is_radar"]:
                has_sar = True
            else:
                has_optical = True
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to scan '{file.filename}': {str(e)}")
            
    # Tailor suggested queries and missing modality hints
    suggested_queries = []
    guidance_alerts = []
    
    if len(results) == 1:
        single = results[0]
        if single["is_radar"]:
            suggested_queries = [
                "What is the dominant land cover and surface water extent?",
                "Identify and map the river corridor via specular backscatter",
                "Highlight high-backscatter structural assets and bridges",
                "Check for water saturation and flood boundary"
            ]
            guidance_alerts.append({
                "type": "RADAR_SINGLE",
                "title": "Synthetic Aperture Radar (SAR) Detected",
                "message": (
                    f"Identified {single['radar_stats']['specular_water_pct']}% water body / river corridor "
                    f"and {single['radar_stats']['double_bounce_structure_pct']}% structural double-bounce returns. "
                    "Single-band SAR penetrates clouds and maps water/geometry with high reliability."
                ),
                "action_prompt": "To unlock multi-spectral vegetation indices (NDVI) or crop classification, upload an Optical companion image!"
            })
        else:
            suggested_queries = [
                "Describe dominant land cover and vegetation density",
                "Highlight surface water bodies and reservoirs",
                "Assess agricultural canopy and built-up infrastructure",
                "Detect runways or transportation corridors"
            ]
            guidance_alerts.append({
                "type": "OPTICAL_SINGLE",
                "title": "Multispectral Optical Imagery Detected",
                "message": "Rich multispectral bands detected. Optimal for land-cover classification and visual QA.",
                "action_prompt": "Upload a Sentinel-1 SAR companion image if all-weather cloud penetration is needed."
            })
    elif len(results) == 2:
        if has_sar and has_optical:
            suggested_queries = [
                "Perform cross-modal Optical+SAR fusion to map land cover and water",
                "Verify water bodies through optical shadows and radar backscatter",
                "Differentiate dense canopy from urban structures using combined indices"
            ]
            guidance_alerts.append({
                "type": "FUSION_READY",
                "title": "Cross-Modal Pair Detected (Optical + SAR)",
                "message": "Perfect pair! 1 Optical MSI and 1 SAR radar scene detected. Ready for full cloud-penetrating fusion.",
                "action_prompt": "Ready to execute Optical-SAR Fusion Analysis."
            })
        else:
            suggested_queries = [
                "Detect what changed between these two temporal dates",
                "Quantify built-up expansion or deforestation rate",
                "Highlight areas of significant spatial difference"
            ]
            guidance_alerts.append({
                "type": "TEMPORAL_READY",
                "title": "Bi-Temporal Pair Detected",
                "message": "Two scenes detected with identical modalities. Ready for Bi-Temporal Change Detection and Change VQA.",
                "action_prompt": "Ready to execute Bi-Temporal Change Detection."
            })
            
    return {
        "file_count": len(results),
        "modalities": results,
        "suggested_queries": suggested_queries,
        "guidance_alerts": guidance_alerts
    }


@router.post("/analyze")
async def analyze_endpoint(
    query: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Unified analysis endpoint executing the agentic remote sensing pipeline.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    if not files:
        raise HTTPException(status_code=400, detail="At least one satellite image file must be uploaded.")
        
    images = []
    metadata_list = []
    
    for file in files:
        contents = await file.read()
        try:
            arr, meta = load_raster(contents)
            images.append(arr)
            metadata_list.append(meta)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read image '{file.filename}': {str(e)}")
            
    try:
        result = execute_agent_pipeline(query, images, metadata_list)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
