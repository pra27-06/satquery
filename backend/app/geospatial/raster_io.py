"""Raster loading utilities for the SatQuery MVP.

Important: PNG/JPEG pixels do not contain trustworthy CRS, GSD, satellite
sensor, acquisition date, or product-level metadata. The MVP therefore does
not invent those values.
"""

import base64
import io
from pathlib import Path
from typing import Tuple, Dict, Any, Union
import numpy as np
from PIL import Image

def load_raster(source: Union[str, Path, bytes, Image.Image]) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Load a standard image into a uint8 RGB array.

    Geospatial metadata is intentionally left unknown for ordinary image
    uploads. A production GeoTIFF/remote-sensing ingestion path should read
    CRS, transform and resolution from the source dataset.
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
        "width": w, "height": h, "channels": c,
        "crs": None, "resolution_meters": None,
        "format": "image/raster",
        "geospatial_metadata_available": False,
        "metadata_note": "No CRS/GSD inferred from PNG/JPEG pixels."
    }
    return arr, metadata

def array_to_base64_png(arr: np.ndarray) -> str:
    if arr.ndim == 2:
        img = Image.fromarray(arr, mode="L")
    elif arr.ndim == 3 and arr.shape[2] == 4:
        img = Image.fromarray(arr, mode="RGBA")
    else:
        img = Image.fromarray(arr, mode="RGB")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

def encode_mask_overlay(base_arr: np.ndarray, mask: np.ndarray, color=(255, 0, 0), alpha=0.45) -> str:
    overlay = base_arr.copy().astype(np.float32)
    mask_bool = mask > 128
    for c in range(3):
        overlay[:, :, c] = np.where(mask_bool,
            overlay[:, :, c] * (1 - alpha) + color[c] * alpha,
            overlay[:, :, c])
    return array_to_base64_png(np.clip(overlay, 0, 255).astype(np.uint8))
