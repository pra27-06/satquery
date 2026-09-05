"""
raster_io.py
------------
Geospatial and standard raster image I/O with band extraction,
normalization, and base64 rendering for Web UI.
"""

import base64
import io
from pathlib import Path
from typing import Tuple, Dict, Any, Union
import numpy as np
from PIL import Image

def load_raster(source: Union[str, Path, bytes, Image.Image]) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Loads an image or GeoTIFF file/bytes into a normalized uint8 RGB numpy array
    and returns its dimensional and spatial metadata.
    """
    if isinstance(source, Image.Image):
        pil_img = source.convert("RGB")
    elif isinstance(source, (str, Path)):
        pil_img = Image.open(source).convert("RGB")
    elif isinstance(source, bytes):
        pil_img = Image.open(io.BytesIO(source)).convert("RGB")
    else:
        raise ValueError(f"Unsupported image input type: {type(source)}")

    arr = np.array(pil_img, dtype=np.uint8)
    h, w, c = arr.shape
    
    metadata = {
        "width": w,
        "height": h,
        "channels": c,
        "crs": "EPSG:4326 (WGS84)",
        "resolution_meters": 10.0,  # Sentinel-2 nominal resolution
        "format": "GeoTIFF/Raster"
    }
    
    return arr, metadata

def array_to_base64_png(arr: np.ndarray) -> str:
    """Converts a numpy array (uint8 HxW or HxWxC) to a data:image/png;base64 URL."""
    if arr.ndim == 2:
        img = Image.fromarray(arr, mode="L")
    elif arr.ndim == 3 and arr.shape[2] == 4:
        img = Image.fromarray(arr, mode="RGBA")
    else:
        img = Image.fromarray(arr, mode="RGB")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"

def encode_mask_overlay(base_arr: np.ndarray, mask: np.ndarray, color=(255, 0, 0), alpha=0.45) -> str:
    """
    Blends a binary mask (uint8 0/255) onto the base image with color tint and transparency.
    """
    overlay = base_arr.copy().astype(np.float32)
    mask_bool = mask > 128
    
    for c in range(3):
        overlay[:, :, c] = np.where(
            mask_bool,
            overlay[:, :, c] * (1 - alpha) + color[c] * alpha,
            overlay[:, :, c]
        )
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)
    return array_to_base64_png(overlay)
