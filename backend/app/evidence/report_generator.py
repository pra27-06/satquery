"""
report_generator.py
--------------------
Generates auditable evidence reports in JSON and interactive printable HTML format
for evaluation by hackathon judges, defense operators, and remote sensing engineers.
Features direct new-tab browser rendering, dual print/download controls, and deep
engineering telemetry.
"""

import json
from datetime import datetime
from typing import Dict, Any

def generate_evidence_report(
    session_id: str,
    query: str,
    classification: Dict[str, Any],
    validation_info: Dict[str, Any],
    tool_results: Dict[str, Any],
    confidence: Dict[str, Any],
    trace_log: list
) -> Dict[str, Any]:
    """
    Compiles full execution provenance into an auditable evidence package
    with deep engineering metrics and interactive export capabilities.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    report_id = f"SATQUERY-EVID-{session_id[:8].upper()}"
    
    # Extract deep telemetry if available
    eng_telemetry = tool_results.get("engineering_telemetry", {})
    modality_info = tool_results.get("modality_info", {})
    spatial_metrics = modality_info.get("spatial_metrics", {})
    band_telemetry = modality_info.get("band_telemetry", [])
    
    report_dict = {
        "report_id": report_id,
        "session_id": session_id,
        "problem_statement": "SIH26167: SatQuery AI (ISRO)",
        "copyright": "Copyright (c) 2026 SatQuery AI. All rights reserved.",
        "generated_at": timestamp,
        "query": query,
        "agentic_plan": classification,
        "input_validation": validation_info,
        "tool_results": {k: v for k, v in tool_results.items() if not k.endswith("_url")},
        "engineering_telemetry": eng_telemetry,
        "confidence_audit": confidence,
        "execution_trace": trace_log
    }
    
    # Render Band Telemetry Table HTML
    band_rows_html = ""
    if band_telemetry:
        for b in band_telemetry:
            band_rows_html += f"""
            <tr>
                <td style="font-weight: 600; color: #38bdf8;">{b.get('band')}</td>
                <td>{b.get('min')}</td>
                <td>{b.get('max')}</td>
                <td style="font-weight: 600;">{b.get('mean')}</td>
                <td>{b.get('std')}</td>
                <td>{b.get('median')}</td>
                <td>{b.get('dynamic_range')}</td>
                <td style="color: #4ade80;">{b.get('snr_db')} dB</td>
                <td style="color: #c084fc;">{b.get('entropy_bits')} bits</td>
            </tr>
            """
            
    # Render Spectral/Radar Distribution Table HTML
    distribution_rows_html = ""
    spectral_dist = tool_results.get("spectral_distribution", {})
    for cls, pct in spectral_dist.items():
        distribution_rows_html += f"""
        <tr>
            <td style="color: #f4f4f5; font-weight: 500;">{cls}</td>
            <td style="font-family: monospace; font-weight: 700; color: #38bdf8;">{pct}%</td>
        </tr>
        """
        
    # Deep SAR or Optical summary block
    radar_diag_html = ""
    if eng_telemetry.get("calibrated_backscatter_sigma0_db"):
        bs = eng_telemetry["calibrated_backscatter_sigma0_db"]
        hg = eng_telemetry.get("hydrological_geometry", {})
        radar_diag_html = f"""
        <div class="card" style="border-left: 4px solid #06b6d4;">
            <div class="field-label" style="color: #22d3ee;">Radar Physics & Calibrated Backscatter Telemetry</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 12px;">
                <div class="stat-box">
                    <div class="stat-label">Specular Water σ⁰</div>
                    <div class="stat-val" style="color: #38bdf8;">{bs.get('specular_water_mean')} dB</div>
                    <div class="stat-sub">Threshold: {bs.get('specular_threshold_limit')} dB</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Diffuse Terrain σ⁰</div>
                    <div class="stat-val" style="color: #a1a1aa;">{bs.get('diffuse_terrain_mean')} dB</div>
                    <div class="stat-sub">Rough surface scatter</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Double-Bounce Assets σ⁰</div>
                    <div class="stat-val" style="color: #f59e0b;">+{bs.get('double_bounce_structure_mean')} dB</div>
                    <div class="stat-sub">Corner reflectors</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Looks / Sinuosity</div>
                    <div class="stat-val" style="color: #c084fc;">ENL: {eng_telemetry.get('equivalent_number_of_looks_enl')}</div>
                    <div class="stat-sub">Sinuosity: {hg.get('sinuosity_index', '1.0')}</div>
                </div>
            </div>
            {f"<div style='margin-top: 12px; font-size: 13px; color: #a1a1aa;'>Estimated River Corridor Length: <strong style='color:#fff;'>{hg.get('estimated_channel_length_km')} km</strong> · Mean Hydraulic Width: <strong style='color:#fff;'>{hg.get('mean_channel_width_m')} m</strong> · Water Area: <strong style='color:#fff;'>{hg.get('water_surface_area_km2')} km²</strong></div>" if hg else ""}
        </div>
        """
    elif eng_telemetry.get("spectral_indices"):
        si = eng_telemetry["spectral_indices"]
        radar_diag_html = f"""
        <div class="card" style="border-left: 4px solid #10b981;">
            <div class="field-label" style="color: #34d399;">Optical Multispectral Index Telemetry</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 12px;">
                <div class="stat-box">
                    <div class="stat-label">Mean NDVI</div>
                    <div class="stat-val" style="color: #4ade80;">{si.get('ndvi_mean')}</div>
                    <div class="stat-sub">Peak P90: {si.get('ndvi_p90_peak')}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Mean NDWI</div>
                    <div class="stat-val" style="color: #38bdf8;">{si.get('ndwi_mean')}</div>
                    <div class="stat-sub">Water index</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Chlorophyll Absorption</div>
                    <div class="stat-val" style="color: #fbbf24;">{si.get('canopy_chlorophyll_absorption_ratio')}x</div>
                    <div class="stat-sub">Green/Red ratio</div>
                </div>
            </div>
        </div>
        """

    # Trace steps
    trace_rows = "".join(
        f"<tr><td>{s.get('step_id')}</td><td style='font-family:monospace; color:#38bdf8;'>+{s.get('timestamp_ms')}ms</td><td class='trace-tag'>[{s.get('stage')}]</td><td>{s.get('message')}</td></tr>"
        for s in trace_log
    )

    # Standalone HTML report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SatQuery AI — Execution Audit Report [{report_id}]</title>
    <style>
        :root {{
            --bg-color: #09090b;
            --card-bg: #111115;
            --border-color: #27272a;
            --text-primary: #f4f4f5;
            --text-secondary: #a1a1aa;
            --accent: #38bdf8;
            --accent-green: #4ade80;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-color);
            color: var(--text-primary);
            padding: 24px;
            max-width: 1200px;
            margin: 0 auto;
            line-height: 1.5;
        }}
        /* Action Top Bar */
        .action-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #18181b;
            border: 1px solid var(--border-color);
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}
        .action-bar .brand {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            font-size: 14px;
            color: #fff;
        }}
        .action-buttons {{
            display: flex;
            gap: 10px;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.15s ease;
        }}
        .btn-primary {{
            background: #0284c7;
            color: #fff;
            border: 1px solid #38bdf8;
        }}
        .btn-primary:hover {{ background: #0369a1; }}
        .btn-secondary {{
            background: #27272a;
            color: #e4e4e7;
            border: 1px solid #3f3f46;
        }}
        .btn-secondary:hover {{ background: #3f3f46; color: #fff; }}
        
        .header {{
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}
        h1 {{ font-size: 26px; color: #ffffff; font-weight: 700; letter-spacing: -0.02em; }}
        .meta-line {{ color: var(--text-secondary); font-size: 13px; margin-top: 4px; }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .field-label {{
            color: var(--text-secondary);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
            margin-bottom: 6px;
        }}
        .field-val {{
            color: var(--text-primary);
            font-size: 15px;
            line-height: 1.6;
        }}
        
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .stat-box {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 12px 14px;
        }}
        .stat-label {{ font-size: 11px; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.05em; }}
        .stat-val {{ font-size: 20px; font-weight: 700; color: #fff; margin-top: 2px; font-family: monospace; }}
        .stat-sub {{ font-size: 10px; color: #71717a; margin-top: 2px; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }}
        th, td {{
            text-align: left;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border-color);
            font-size: 13px;
        }}
        th {{
            color: var(--text-secondary);
            background: #141418;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        .trace-tag {{ color: var(--accent); font-family: monospace; font-size: 12px; font-weight: 600; }}
        
        /* Print Stylesheet */
        @media print {{
            body {{ background: #fff !important; color: #000 !important; padding: 12px; }}
            .action-bar {{ display: none !important; }}
            .card {{ background: #fff !important; border: 1px solid #ccc !important; color: #000 !important; break-inside: avoid; }}
            .field-val {{ color: #000 !important; }}
            .stat-box {{ background: #f4f4f5 !important; border: 1px solid #ddd !important; }}
            .stat-val {{ color: #000 !important; }}
            th {{ background: #f4f4f5 !important; color: #333 !important; }}
            td {{ color: #000 !important; border-bottom: 1px solid #ddd !important; }}
        }}
    </style>
</head>
<body>
    <!-- Action Bar for Viewer -->
    <div class="action-bar">
        <div class="brand">
            <span>🛰️ SatQuery AI Evidence System</span>
            <span style="font-size: 11px; background: #27272a; padding: 2px 8px; border-radius: 4px; color: #38bdf8;">ISRO SIH26167</span>
        </div>
        <div class="action-buttons">
            <button onclick="window.print()" class="btn btn-secondary">
                🖨️ Print / Save to PDF
            </button>
            <button onclick="downloadHtmlFile()" class="btn btn-primary">
                📥 Download HTML Report
            </button>
        </div>
    </div>

    <div class="header">
        <span class="badge">Verified Autonomous Remote Sensing Audit</span>
        <h1>SatQuery AI — Observable Evidence Report</h1>
        <div class="meta-line">
            Report ID: <strong style="color: #fff; font-family: monospace;">{report_id}</strong> &middot; Generated: {timestamp} &middot; Session: {session_id}
        </div>
    </div>
    
    <!-- User Query & Execution Plan -->
    <div class="card">
        <div class="field-label">Natural Language Inquiry</div>
        <div class="field-val" style="font-size: 18px; font-weight: 600; color: #38bdf8;">"{query}"</div>
        <div class="grid-3">
            <div class="stat-box">
                <div class="stat-label">Classified Task</div>
                <div class="stat-val" style="font-size: 15px;">{classification.get('task')}</div>
                <div class="stat-sub">{classification.get('description')}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Specialist Tool</div>
                <div class="stat-val" style="font-size: 15px; color: #38bdf8;">{classification.get('tool_name')}</div>
                <div class="stat-sub">Deterministic compute</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Dual-Estimate Confidence</div>
                <div class="stat-val" style="color: #4ade80;">{confidence.get('confidence_percentage')}</div>
                <div class="stat-sub">{confidence.get('rating')}</div>
            </div>
        </div>
    </div>

    <!-- Synthesis & Grounded Finding -->
    <div class="card">
        <div class="field-label">Evidence-Grounded Synthesis</div>
        <div class="field-val" style="white-space: pre-line; margin-top: 6px; font-size: 15px; border-left: 3px solid #38bdf8; padding-left: 14px;">
{tool_results.get('answer')}
        </div>
    </div>

    <!-- Radar / Optical Deep Physics Block -->
    {radar_diag_html}

    <!-- Land Cover / Spectral Distribution -->
    {f'''
    <div class="card">
        <div class="field-label">Surface Feature Distribution (GSD: {spatial_metrics.get('ground_sampling_distance_m', 10.0)}m/px &middot; Total: {spatial_metrics.get('total_area_km2', 'N/A')} km²)</div>
        <table>
            <thead>
                <tr>
                    <th>Class Name / Feature</th>
                    <th>Surface Area Coverage</th>
                </tr>
            </thead>
            <tbody>
                {distribution_rows_html}
            </tbody>
        </table>
    </div>
    ''' if distribution_rows_html else ''}

    <!-- Band Radiometric Telemetry Table -->
    {f'''
    <div class="card">
        <div class="field-label">Deep Engineering Radiometric Band Telemetry</div>
        <div style="font-size: 12px; color: #a1a1aa; margin-bottom: 8px;">Exhaustive statistical, radiometric, and signal-to-noise metrics per spectral band:</div>
        <table>
            <thead>
                <tr>
                    <th>Band</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Mean</th>
                    <th>Std Dev</th>
                    <th>Median</th>
                    <th>Dynamic Range</th>
                    <th>SNR (dB)</th>
                    <th>Shannon Entropy</th>
                </tr>
            </thead>
            <tbody>
                {band_rows_html}
            </tbody>
        </table>
    </div>
    ''' if band_rows_html else ''}

    <!-- Step-by-Step Agentic Trace -->
    <div class="card">
        <div class="field-label">Verifiable Agentic Execution Trace (Auditable Latencies)</div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Latency</th>
                    <th>Stage</th>
                    <th>Action / Observable Output</th>
                </tr>
            </thead>
            <tbody>
                {trace_rows}
            </tbody>
        </table>
    </div>

    <div style="margin-top: 32px; border-top: 1px solid var(--border-color); padding-top: 16px; text-align: center; color: #71717a; font-size: 12px;">
        &copy; 2026 <strong>SatQuery AI</strong>. All rights reserved. &middot; SIH26167 SatQuery AI Platform
    </div>

    <script>
        function downloadHtmlFile() {{
            const htmlContent = '<!DOCTYPE html>' + document.documentElement.outerHTML;
            const blob = new Blob([htmlContent], {{ type: 'text/html' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{report_id}.html';
            a.click();
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
"""
    return {
        "data": report_dict,
        "html": html_content
    }
