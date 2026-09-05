"""
generate_samples.py
-------------------
Fetches authentic European Space Agency (ESA) Sentinel-1 and Sentinel-2
Earth Observation satellite imagery and RSVQA benchmarks for the 5 SIH evaluation scenarios.
"""

from pathlib import Path
import urllib.request
import io
from PIL import Image

SAMPLES_DIR = Path(__file__).resolve().parent / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0'}
BASE_URL = 'https://raw.githubusercontent.com/VaibhavUPratap/SatQuery-SIH/main/samples/'

DATA_MAP = {
    # Demo 1: Real Sentinel-2 River & Farmland optical scene
    'optical_single.png': 'optical_sar/pair2_river_farmland_sentinel2_optical.png',
    # Demo 2: Real RSVQA Benchmark scene with structures and hydrological features
    'grounding_scene.png': 'vqa/rsvqa_sample_0.png',
    # Demos 3 & 4: Real Sentinel-2 Bi-Temporal Urban Growth Pair
    'temporal_t1.png': 'temporal/change_02_urban_growth_t1.png',
    'temporal_t2.png': 'temporal/change_02_urban_growth_t2.png',
    # Demo 5: Real Co-registered Sentinel-2 Optical + Sentinel-1 SAR Radar Coastal Port
    'optical_fusion.png': 'optical_sar/pair1_coastal_port_sentinel2_optical.png',
    'sar_fusion.png': 'optical_sar/pair1_coastal_port_sentinel1_sar.png',
}

def download_real_satellite_samples():
    print("Downloading authentic Sentinel-1 & Sentinel-2 satellite imagery...")
    for target_name, rel_path in DATA_MAP.items():
        url = BASE_URL + rel_path
        target_path = SAMPLES_DIR / target_name
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                im = Image.open(io.BytesIO(resp.read())).convert('RGB')
                im = im.resize((512, 512), Image.Resampling.BICUBIC)
                im.save(target_path)
                print(f"  ✓ Saved real satellite image: {target_name} (512x512)")
        except Exception as e:
            print(f"  ✗ Error downloading {target_name}: {e}")

if __name__ == "__main__":
    download_real_satellite_samples()
