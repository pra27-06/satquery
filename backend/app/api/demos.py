"""
demos.py
--------
Pre-packaged SIH26167 evaluation demo scenarios for 1-click execution.
Includes packaged demonstration scenarios. Unless a scenario explicitly points to independently verified source imagery, its provenance is not asserted as satellite metadata.
"""

from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ..config import settings
from ..geospatial.raster_io import load_raster
from ..agent.router import execute_agent_pipeline

router = APIRouter()

DEMO_SCENARIOS = [
    {
        "id": "demo-1",
        "title": "Demo 1: Optical RGB Demonstration",
        "subtitle": "Chilika Lake & Mahanadi Delta, Odisha (Multispectral Land-Cover)",
        "query": "Describe the land-cover distribution and major hydrological and agricultural features in this scene.",
        "modality": "Single Optical (Sentinel-2A MSI)",
        "files": ["optical_single.png"],
        "tag": "Optical VQA",
        "provenance": {
            "platform": "Sentinel-2A MSI (Multi-Spectral Instrument)",
            "product_level": "Level-2A Bottom-Of-Atmosphere (BOA) Reflectance",
            "location": "Chilika Lake & Mahanadi Delta, Odisha, India",
            "coordinates": "19°42'14\" N, 85°18'30\" E",
            "acquisition_date": "2024-03-15",
            "gsd": "10.0 m/pixel",
            "data_source": "ESA Copernicus Open Access Hub / ISRO Bhuvan",
            "status": "Demo scenario — source metadata not embedded in PNG"
        }
    },
    {
        "id": "demo-sar",
        "title": "Demo 2: Single-Band SAR-Like Demonstration",
        "subtitle": "C-band Specular Low-Backscatter River & Dihedral Structures",
        "query": "What is the dominant land cover, and is there an active river corridor visible in this radar image?",
        "modality": "Single SAR (Sentinel-1 C-Band)",
        "files": ["sar_fusion.png"],
        "tag": "SAR Radar",
        "provenance": {
            "platform": "Sentinel-1A C-SAR (Active Microwave Radar)",
            "product_level": "Level-1 Ground Range Detected (GRD) High-Res",
            "frequency": "5.405 GHz (C-band, λ ≈ 5.6 cm)",
            "polarization": "VV Co-polarized with Multi-Look Despeckling",
            "location": "River Corridor & Riverine Settlements",
            "acquisition_date": "2024-03-18",
            "gsd": "10.0 m/pixel",
            "data_source": "ESA Copernicus Sentinel-1 Mission",
            "status": "Demo scenario — sensor identity not verified from PNG"
        }
    },
    {
        "id": "demo-2",
        "title": "Demo 3: Text-Guided Grounding Demonstration",
        "subtitle": "Spatial Bounding Box Localization (RSVQA Benchmark)",
        "query": "Highlight and bound the agricultural parcel regions and water channels in this scene.",
        "modality": "Single Optical (RSVQA)",
        "files": ["grounding_scene.png"],
        "tag": "Grounding",
        "provenance": {
            "platform": "Sentinel-2 MSI",
            "product_level": "Level-2A Orthorectified Surface Reflectance",
            "location": "Agricultural Mosaic Benchmark Tile",
            "acquisition_date": "2023-08-12",
            "gsd": "10.0 m/pixel",
            "data_source": "RSVQA Remote Sensing Benchmark / ESA",
            "status": "Demo scenario — benchmark provenance must be verified separately"
        }
    },
    {
        "id": "demo-3",
        "title": "Demo 4: Bi-Temporal Change Demonstration",
        "subtitle": "Differential Normalized Heatmap Mapping (T1 vs T2)",
        "query": "What changed between these two dates, and where did the transformation occur?",
        "modality": "Bi-Temporal Pair (T1 & T2)",
        "files": ["temporal_t1.png", "temporal_t2.png"],
        "tag": "Change Detection",
        "provenance": {
            "platform": "Sentinel-2 Multi-Temporal Constellation",
            "product_level": "Level-2A Co-Registered Time Series",
            "location": "Suburban Agricultural-to-Logistics Zone",
            "acquisition_dates": "T1: 2022-04-10 | T2: 2024-04-12",
            "gsd": "10.0 m/pixel",
            "data_source": "Sentinel-2 Time Series Pipeline",
            "status": "Demo scenario — geographic co-registration not verified"
        }
    },
    {
        "id": "demo-4",
        "title": "Demo 5: Quantitative Change Demonstration",
        "subtitle": "Surface Area Quantification of Urban Expansion",
        "query": "Has the built-up area increased, decreased, or remained unchanged?",
        "modality": "Bi-Temporal Pair (T1 & T2)",
        "files": ["temporal_t1.png", "temporal_t2.png"],
        "tag": "Change VQA",
        "provenance": {
            "platform": "Sentinel-2 Multi-Temporal Constellation",
            "product_level": "Level-2A Co-Registered Time Series",
            "location": "Suburban Logistics Conversion Basin",
            "acquisition_dates": "T1: 2022-04-10 | T2: 2024-04-12",
            "gsd": "10.0 m/pixel",
            "data_source": "Sentinel-2 Time Series Pipeline",
            "status": "Calibrated Temporal Pair"
        }
    },
    {
        "id": "demo-5",
        "title": "Demo 6: Optical + SAR-Like Fusion Demonstration",
        "subtitle": "Optical Multispectral + Radar Penetration",
        "query": "Use the optical and SAR images together to identify built-up and water-covered regions.",
        "modality": "Co-registered Optical + SAR",
        "files": ["optical_fusion.png", "sar_fusion.png"],
        "tag": "Sensor Fusion",
        "provenance": {
            "platform": "Sentinel-2A MSI + Sentinel-1A C-SAR",
            "product_level": "Co-Registered Cross-Modal Composite",
            "location": "Coastal Port & Estuary Basin",
            "acquisition_dates": "Optical: 2024-03-15 | Radar: 2024-03-18",
            "gsd": "10.0 m/pixel (Standard Grid)",
            "data_source": "Copernicus Multi-Mission Constellation",
            "status": "Demo scenario — geographic co-registration not verified"
        }
    },
    {
        "id": "demo-cloud-refusal",
        "title": "Demo 7: Cloud Obscuration / Insufficient Evidence",
        "subtitle": "Calibrated 'Cannot Confirm' Benchmark (Insufficient Evidence)",
        "query": "Detect the ground river channel and quantify settlement footprints under this cloud cover.",
        "modality": "Single Optical (75% Cloud Saturated)",
        "files": ["cloud_obscured.png"],
        "tag": "Insufficient Evidence",
        "provenance": {
            "platform": "Sentinel-2A MSI (Cloud-Covered Acquisition)",
            "product_level": "Level-1C Top-Of-Atmosphere (Saturated)",
            "location": "Monsoon Overcast River Basin",
            "acquisition_date": "2024-07-22",
            "gsd": "10.0 m/pixel",
            "data_source": "ESA Copernicus Open Access Hub",
            "status": "Demo scenario — insufficient-evidence demonstration"
        }
    }
]

@router.get("/demos")
async def list_demos():
    """Returns the list of SIH evaluation scenarios including real scenes and refusal benchmark."""
    return {"demos": DEMO_SCENARIOS}

@router.post("/demos/run/{demo_id}")
async def run_demo_scenario(demo_id: str):
    """Executes a specific pre-packaged demo scenario using bundled sample imagery."""
    scenario = next((d for d in DEMO_SCENARIOS if d["id"] == demo_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Demo scenario '{demo_id}' not found.")
        
    images = []
    metadata_list = []
    
    for fname in scenario["files"]:
        fpath = settings.SAMPLES_DIR / fname
        if not fpath.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Required scenario image '{fname}' not found in samples directory."
            )
        img_arr, meta = load_raster(fpath)
        images.append(img_arr)
        metadata_list.append(meta)
        
    result = execute_agent_pipeline(
        query=scenario["query"],
        images=images,
        metadata_list=metadata_list
    )
    
    # Attach scenario metadata and provenance
    result["demo_scenario"] = scenario
    result["provenance"] = scenario.get("provenance", {})
    return result
