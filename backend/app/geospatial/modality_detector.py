"""
modality_detector.py
--------------------
Automated Sensor & Modality Detection Engine for SatQuery AI.
Analyzes channel statistics, spectral variance, speckle noise, and radiometric
telemetry to distinguish Synthetic Aperture Radar (SAR) from Optical Multispectral
imagery with exhaustive spatial, radiometric, and geodetic measurements.
"""

from typing import Dict, Any, List
import numpy as np

def compute_band_stats(band: np.ndarray, band_name: str) -> Dict[str, Any]:
    """Computes comprehensive engineering radiometric statistics for a single raster band."""
    arr = band.astype(np.float32)
    b_min = float(np.min(arr))
    b_max = float(np.max(arr))
    b_mean = float(np.mean(arr))
    b_std = float(np.std(arr))
    b_median = float(np.median(arr))
    p10 = float(np.percentile(arr, 10))
    p90 = float(np.percentile(arr, 90))
    dynamic_range = float(b_max - b_min)
    
    # Signal-to-Noise Ratio (SNR) in dB
    snr_linear = (b_mean / (b_std + 1e-5))
    snr_db = round(float(20 * np.log10(max(1e-3, snr_linear))), 2)
    
    # Shannon Entropy (Information content in bits)
    hist, _ = np.histogram(arr, bins=64, range=(0, 256))
    hist_prob = hist / (np.sum(hist) + 1e-7)
    hist_prob = hist_prob[hist_prob > 0]
    entropy = round(float(-np.sum(hist_prob * np.log2(hist_prob))), 3)
    
    return {
        "band": band_name,
        "min": round(b_min, 1),
        "max": round(b_max, 1),
        "mean": round(b_mean, 2),
        "std": round(b_std, 2),
        "median": round(b_median, 1),
        "p10": round(p10, 1),
        "p90": round(p90, 1),
        "dynamic_range": round(dynamic_range, 1),
        "snr_db": snr_db,
        "entropy_bits": entropy
    }

def detect_modality(img: np.ndarray) -> Dict[str, Any]:
    """
    Analyzes an input satellite raster tensor and returns its modality,
    sensor characteristics, feature breakdown, and deep radiometric engineering metrics.
    """
    if img.ndim == 2:
        h, w = img.shape
        c = 1
        gray = img.astype(np.float32)
        channel_diff = 0.0
        bands = [compute_band_stats(gray, "Intensity (Band 1)")]
    elif img.ndim == 3:
        h, w, c = img.shape
        if c == 1:
            gray = img[:, :, 0].astype(np.float32)
            channel_diff = 0.0
            bands = [compute_band_stats(gray, "Intensity (Band 1)")]
        else:
            r = img[:, :, 0].astype(np.float32)
            g = img[:, :, 1].astype(np.float32)
            b = img[:, :, 2].astype(np.float32)
            gray = (0.299 * r + 0.587 * g + 0.114 * b)
            channel_diff = float(np.mean(np.abs(r - g) + np.abs(g - b) + np.abs(b - r)))
            bands = [
                compute_band_stats(r, "Red (Band 4)"),
                compute_band_stats(g, "Green (Band 3)"),
                compute_band_stats(b, "Blue (Band 2)")
            ]
    else:
        raise ValueError(f"Unsupported image dimensions: {img.shape}")

    total_pixels = h * w
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    speckle_index = float(std_val / (mean_val + 1e-5))
    
    # Check if grayscale (or identical RGB channels)
    is_single_band_or_gray = (c == 1) or (channel_diff < 1.5)
    
    # Spatial Metrics (Sentinel constellation standard: 10m GSD)
    gsd_meters = None
    pixel_area_m2 = None
    total_area_km2 = None
    total_hectares = None

    # Radar Physics Feature Extraction
    water_mask = (gray < 42)
    water_pct = round(float(np.sum(water_mask) / total_pixels * 100), 2)
    water_area_km2 = round((water_pct / 100) * total_area_km2, 3)
    
    structure_mask = (gray > 140)
    structure_pct = round(float(np.sum(structure_mask) / total_pixels * 100), 2)
    structure_area_km2 = round((structure_pct / 100) * total_area_km2, 3)
    
    terrain_mask = (~water_mask) & (~structure_mask)
    terrain_pct = round(float(np.sum(terrain_mask) / total_pixels * 100), 2)
    terrain_area_km2 = round((terrain_pct / 100) * total_area_km2, 3)

    if is_single_band_or_gray:
        modality = "SAR_RADAR"
        sensor_family = "Single-band / grayscale raster (sensor not verified)"
        sensor_derivation = (
            f"Derived via Radiometric Distribution: Single-channel amplitude distribution "
            f"(mean: {np.mean(gray):.1f}, std: {np.std(gray):.1f}, speckle index: {speckle_index:.2f}) "
            f"This pixel statistic alone is not sufficient to identify Sentinel-1 or calibrated SAR data."
        )
        is_radar = True
        
        has_river = water_pct > 15.0
        has_urban = structure_pct > 10.0
        
        recommendations = []
        if has_river:
            recommendations.append(
                f"Prominent water body / river corridor detected ({water_pct}% / {water_area_km2} km²) "
                f"via low radar backscatter consistent with specular reflection away from the satellite sensor. "
                f"(Physical note: Smooth water acts as a specular reflector directing microwave energy away from the radar antenna. "
                f"Note that other flat smooth surfaces—such as airport runways or dry sands—can exhibit similar low backscatter, "
                f"while wind-roughened water surfaces may show elevated backscatter due to Bragg scattering.)"
            )
        if has_urban:
            recommendations.append(
                f"Elevated microwave backscatter detected ({structure_pct}% / {structure_area_km2} km²), "
                f"consistent with dihedral corner-reflector interactions between orthogonal structural walls and the ground plane."
            )
            
        recommendations.append(
            "Sensor guidance: Single-band SAR penetrates persistent cloud cover and delineates surface water geometry, "
            "but lacks multispectral Red/NIR bands for photosynthetic vigor (NDVI) or crop species classification."
        )
        
        missing_modalities = [
            {
                "modality": "OPTICAL_RGB",
                "recommended_for": "Cross-Modal Optical+SAR Fusion (enables cloud-penetrating crop & land-use verification)",
                "action": "Upload an Optical (Sentinel-2 or Landsat) co-registered companion image"
            }
        ]
    else:
        modality = "OPTICAL_RGB"
        sensor_family = "RGB-like optical image (sensor not verified)"
        sensor_derivation = (
            f"Derived via Multispectral Ratio: 3-channel visible spectrum "
            f"(inter-channel variance: {channel_diff:.1f}) "
            f"This pixel statistic alone is not sufficient to identify Sentinel-2/Landsat or multispectral bands."
        )
        is_radar = False
        
        recommendations = [
            f"Multispectral visible color channels detected ({total_area_km2} km² coverage). Optimal for land-cover classification, vegetation indices, and visual QA."
        ]
        missing_modalities = [
            {
                "modality": "SAR_RADAR",
                "recommended_for": "All-weather surface water verification and cloud penetration",
                "action": "Upload a Sentinel-1 SAR companion image for Optical-SAR Fusion"
            }
        ]
        
    return {
        "modality": modality,
        "sensor_family": sensor_family,
        "sensor_derivation": sensor_derivation,
        "is_radar": is_radar,
        "dimensions": f"{w}x{h}",
        "channel_count": c,
        "spectral_variance": round(channel_diff, 2),
        "speckle_index": round(speckle_index, 3),
        "spatial_metrics": {
            "ground_sampling_distance_m": gsd_meters,
            "total_pixels": total_pixels,
            "total_area_km2": total_area_km2,
            "total_hectares": total_hectares,
            "spatial_crs": None,
            "nominal_center": None,
            "metadata_status": "NOT_AVAILABLE_FROM_IMAGE_PIXELS"
        },
        "band_telemetry": bands,
        "radar_stats": {
            "specular_water_pct": water_pct,
            "specular_water_area_km2": None,
            "diffuse_terrain_pct": terrain_pct,
            "diffuse_terrain_area_km2": None,
            "double_bounce_structure_pct": structure_pct,
            "double_bounce_structure_area_km2": None,
            "mean_backscatter_intensity": round(mean_val, 1),
            "estimated_sigma0_db": None,
            "calibrated_backscatter_available": False,
            "analysis_note": "Intensity thresholds are prototype heuristics, not calibrated sigma0."
        },
        "recommendations": recommendations,
        "missing_modalities": missing_modalities
    }
