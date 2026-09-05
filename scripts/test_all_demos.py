"""
test_all_demos.py
-----------------
Automated verification script that executes all mandatory SIH26167
evaluation scenarios plus the new Smart Ingestion SAR River Detection test.
"""

import sys
import time
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.config import settings
from backend.app.geospatial.raster_io import load_raster
from backend.app.agent.router import execute_agent_pipeline

def run_tests():
    print("=" * 70)
    print("🛰️  SATQUERY AI — SIH26167 AUTOMATED EVALUATION SUITE")
    print("=" * 70)
    
    samples_dir = settings.SAMPLES_DIR

    test_cases = [
        {
            "id": "DEMO 1",
            "name": "Single-Image VQA (Optical Land-Cover)",
            "files": ["optical_single.png"],
            "query": "Describe the land-cover and major objects visible in this image.",
            "expected_tool": "single_vqa_tool",
            "assert_fn": lambda res: any("Vegetation" in k for k in res["results"]["spectral_distribution"]) and res["confidence"]["confidence_score"] > 0.85
        },
        {
            "id": "DEMO 1-SAR",
            "name": "Single SAR Radar Ingestion & River Detection (Fixes User Issue)",
            "files": ["sar_fusion.png"],
            "query": "What is the dominant land cover and is there any river visible?",
            "expected_tool": "single_vqa_tool",
            "assert_fn": lambda res: any("Water" in k for k in res["results"]["spectral_distribution"]) and res["results"]["spectral_distribution"][list(res["results"]["spectral_distribution"].keys())[0]] > 10.0
        },
        {
            "id": "DEMO 2",
            "name": "Text-Guided Region Grounding",
            "files": ["grounding_scene.png"],
            "query": "Highlight the water bodies and reservoirs.",
            "expected_tool": "grounding_tool",
            "assert_fn": lambda res: res["results"]["detected_count"] > 0 and len(res["results"]["bounding_boxes"]) > 0
        },
        {
            "id": "DEMO 3",
            "name": "Bi-Temporal Change Detection & Heatmap",
            "files": ["temporal_t1.png", "temporal_t2.png"],
            "query": "What changed between these two dates, and where did the change occur?",
            "expected_tool": "change_detection_tool",
            "assert_fn": lambda res: res["results"]["total_change_percentage"] > 5.0 and "change_heatmap_url" in res["results"]
        },
        {
            "id": "DEMO 4",
            "name": "Quantitative Change VQA",
            "files": ["temporal_t1.png", "temporal_t2.png"],
            "query": "Has the built-up area increased, decreased, or remained unchanged?",
            "expected_tool": "change_vqa_tool",
            "assert_fn": lambda res: "INCREASED" in res["answer"].upper() and res["results"]["urban_gain_percentage"] > 0
        },
        {
            "id": "DEMO 5",
            "name": "Cross-Modal Optical + SAR Cloud Penetration",
            "files": ["optical_fusion.png", "sar_fusion.png"],
            "query": "Use optical and SAR images together to identify built-up and water through cloud cover.",
            "expected_tool": "optical_sar_fusion_tool",
            "assert_fn": lambda res: res["results"]["fused_water_percentage"] > 5.0 and "fused_url" in res["results"]
        },
        {
            "id": "DEMO 7",
            "name": "Cloud-Obscured Ambiguity (Cannot Confirm Refusal Benchmark)",
            "files": ["cloud_obscured.png"],
            "query": "Is there an active river and urban settlement under this cloud cover?",
            "expected_tool": "single_vqa_tool",
            "assert_fn": lambda res: res["results"].get("insufficient_evidence") is True and "CANNOT CONFIRM" in res["answer"] and res["confidence"]["confidence_score"] < 0.50
        }
    ]

    all_passed = True
    total_time = 0.0

    for tc in test_cases:
        print(f"\n▶ Running {tc['id']}: {tc['name']}...")
        images = []
        meta_list = []
        for f in tc["files"]:
            arr, meta = load_raster(samples_dir / f)
            images.append(arr)
            meta_list.append(meta)

        t_start = time.time()
        res = execute_agent_pipeline(tc["query"], images, meta_list)
        elapsed = (time.time() - t_start) * 1000
        total_time += elapsed

        # Assertions
        passed_tool = (res["tool_used"] == tc["expected_tool"])
        passed_custom = tc["assert_fn"](res)

        if passed_tool and passed_custom:
            status_str = "✅ PASSED"
        else:
            status_str = "❌ FAILED"
            all_passed = False

        print(f"  Status:     {status_str}")
        print(f"  Tool Used:  {res['tool_used']}")
        print(f"  Confidence: {res['confidence']['confidence_percentage']} ({res['confidence']['rating']})")
        print(f"  Latency:    {elapsed:.1f}ms")
        print(f"  Answer Snippet: {res['answer'].splitlines()[0][:90]}...")

    print("\n" + "=" * 70)
    if all_passed:
        print(f"🎉 ALL {len(test_cases)} EVALUATION SCENARIOS PASSED! (Avg Latency: {total_time/len(test_cases):.1f}ms)")
    else:
        print("⚠️ SOME TEST SCENARIOS FAILED. REVIEW OUTPUT ABOVE.")
    print("=" * 70)

    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
