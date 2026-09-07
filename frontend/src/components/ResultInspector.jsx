import React, { useState } from 'react';
import { 
  ShieldCheck, 
  FileDown, 
  ExternalLink, 
  BarChart3, 
  Info, 
  AlertTriangle, 
  Radio, 
  Layers, 
  Cpu, 
  Activity, 
  Copy, 
  Check, 
  Compass
} from 'lucide-react';
import { getFullApiUrl } from '../api/client';

function FormattedAnswer({ text }) {
  if (!text) return null;
  const paragraphs = text.split('\n\n');
  return (
    <div className="space-y-2.5 text-sm text-zinc-100 leading-relaxed">
      {paragraphs.map((p, pIdx) => {
        const lines = p.split('\n');
        return (
          <div key={pIdx} className="space-y-1">
            {lines.map((line, lIdx) => {
              const trimmed = line.trim();
              const isBullet = trimmed.startsWith('- ') || trimmed.startsWith('* ');
              const cleanLine = isBullet ? trimmed.slice(2) : line;
              // Parse **bold** into styled spans
              const parts = cleanLine.split(/(\*\*.*?\*\*)/g);
              const renderedParts = parts.map((part, partIdx) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                  return (
                    <strong key={partIdx} className="font-semibold text-white bg-zinc-800/80 px-1 py-0.5 rounded border border-white/10">
                      {part.slice(2, -2)}
                    </strong>
                  );
                }
                return part;
              });

              if (isBullet) {
                return (
                  <div key={lIdx} className="flex items-start gap-2 ml-1">
                    <span className="text-sky-400 mt-1.5 h-1.5 w-1.5 rounded-full bg-sky-400 shrink-0" />
                    <span>{renderedParts}</span>
                  </div>
                );
              }
              return <p key={lIdx}>{renderedParts}</p>;
            })}
          </div>
        );
      })}
    </div>
  );
}

export default function ResultInspector({ result }) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'bands' | 'physics' | 'raw'
  const [copied, setCopied] = useState(false);
  const [showConfidenceDetails, setShowConfidenceDetails] = useState(false);

  if (!result) return null;

  const { 
    answer, 
    confidence, 
    results, 
    report_id, 
    report_html, 
    session_id, 
    modalities, 
    guidance_notes,
    engineering_telemetry,
    report_url
  } = result;

  // Sensor modality info
  const primaryModality = modalities?.[0] || results?.modality_info;
  const isRadar = primaryModality?.is_radar || results?.measured_metrics?.is_radar;
  const spatialMetrics = primaryModality?.spatial_metrics || {};
  const bandTelemetry = primaryModality?.band_telemetry || [];
  const eng = engineering_telemetry || results?.engineering_telemetry || {};

  const handleDownloadReport = () => {
    const blob = new Blob([report_html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report_id || 'satquery_evidence_report'}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleOpenInNewTab = () => {
    const targetUrl = getFullApiUrl(report_url || `/api/report/${session_id}`);
    window.open(targetUrl, '_blank', 'noopener,noreferrer');
  };

  const handleCopyJson = () => {
    const jsonStr = JSON.stringify(result, null, 2);
    navigator.clipboard.writeText(jsonStr);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-2xl border border-zinc-800 bg-[#0c0c0e] shadow-xl flex flex-col overflow-hidden">
      {/* Top Header & Sensor Badge */}
      <div className="p-4 border-b border-zinc-800/80 bg-zinc-900/30 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="flex items-center gap-2.5">
          <div className={`p-1.5 rounded-lg border ${
            isRadar 
              ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' 
              : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
          }`}>
            <Radio className="h-4 w-4" />
          </div>
          <div>
            <div className="text-xs font-semibold text-white tracking-tight">
              {primaryModality?.sensor_family || (isRadar ? 'Sentinel-1 C-Band SAR' : 'Sentinel-2 MSI Optical')}
            </div>
            <div className="text-[11px] text-zinc-400 font-mono">
              Session: {session_id?.slice(0, 8)} &middot; {spatialMetrics?.ground_sampling_distance_m || 10}m GSD
            </div>
          </div>
        </div>

        {/* Dual Actions: View in New Tab & Download */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleOpenInNewTab}
            title="Open comprehensive interactive report in a new browser tab"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 text-xs font-medium transition"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            <span>View in New Tab</span>
          </button>
          <button
            onClick={handleDownloadReport}
            title="Download standalone offline HTML report"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 hover:text-white text-xs font-medium transition"
          >
            <FileDown className="h-3.5 w-3.5" />
            <span>Download</span>
          </button>
        </div>
      </div>

      {/* Tabs Navigation for Desktop */}
      <div className="flex items-center px-4 pt-3 border-b border-zinc-800/80 bg-zinc-950/40 gap-1 overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition border-b-2 ${
            activeTab === 'overview'
              ? 'border-sky-500 text-sky-400 bg-zinc-900/50'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Info className="h-3.5 w-3.5" />
          <span>Overview</span>
        </button>

        <button
          onClick={() => setActiveTab('bands')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition border-b-2 ${
            activeTab === 'bands'
              ? 'border-sky-500 text-sky-400 bg-zinc-900/50'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <BarChart3 className="h-3.5 w-3.5" />
          <span>Band Telemetry</span>
          {bandTelemetry.length > 0 && (
            <span className="px-1.5 py-0.2 rounded text-[10px] bg-zinc-800 text-zinc-400 font-mono">
              {bandTelemetry.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('physics')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition border-b-2 ${
            activeTab === 'physics'
              ? 'border-sky-500 text-sky-400 bg-zinc-900/50'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Compass className="h-3.5 w-3.5" />
          <span>{isRadar ? 'Radar Physics' : 'Spectral Indices'}</span>
        </button>

        <button
          onClick={() => setActiveTab('raw')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition border-b-2 ${
            activeTab === 'raw'
              ? 'border-sky-500 text-sky-400 bg-zinc-900/50'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Cpu className="h-3.5 w-3.5" />
          <span>Raw Audit Matrix</span>
        </button>
      </div>

      {/* Tab Content Body */}
      <div className="p-4 space-y-4 max-h-[680px] overflow-y-auto">
        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Neuro-Symbolic Agent & Engine Role Demarcation */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-xl bg-zinc-900/80 border border-zinc-800 text-[11px]">
              <div className="flex items-center gap-1.5 text-sky-400">
                <span className="font-semibold text-zinc-300">Query Router:</span>
                <span className="font-mono text-sky-300">{result.task_description || result.task}</span>
              </div>
              <div className="flex items-center gap-1.5 text-emerald-400">
                <span className="font-semibold text-zinc-300">Algorithm:</span>
                <span className="font-mono text-emerald-300">{result.tool_used}</span>
              </div>
            </div>

            {/* Answer Block with Clean Markdown Formatting */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                  <Activity className="h-3.5 w-3.5 text-sky-400" />
                  Evidence-Grounded Finding
                </span>
                <span className="text-[11px] text-zinc-500 font-mono">Status: {confidence?.rating || 'Verified'}</span>
              </div>
              <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 shadow-inner">
                <FormattedAnswer text={answer} />
              </div>
            </div>

            {/* Single Deduplicated Sensor Recommendation */}
            {(results?.guidance?.missing_modality_alert || (guidance_notes && guidance_notes.length > 0)) && (
              <div className="p-3.5 rounded-xl bg-amber-950/25 border border-amber-500/40 text-xs space-y-1.5">
                <div className="font-semibold text-amber-300 flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  <span>Actionable Sensor Guidance</span>
                </div>
                <p className="text-zinc-200 text-xs leading-relaxed">
                  {results?.guidance?.missing_modality_alert || guidance_notes[0]}
                </p>
              </div>
            )}

            {/* Confidence Card with Auditable Derivation */}
            <div className="p-3.5 rounded-xl bg-zinc-900/50 border border-zinc-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-emerald-400" />
                  <div>
                    <div className="text-xs text-zinc-400">Dual-Estimate Confidence</div>
                    <div className="text-lg font-bold text-white flex items-baseline gap-2">
                      {confidence?.confidence_percentage || '—'}
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        confidence?.rating?.includes('LOW') 
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' 
                          : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      }`}>
                        {confidence?.rating || 'Evidence status unavailable'}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setShowConfidenceDetails(!showConfidenceDetails)}
                  className="px-2.5 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-[11px] text-sky-400 font-medium border border-zinc-700 transition"
                >
                  {showConfidenceDetails ? 'Hide Calculation' : 'How is this calculated?'}
                </button>
              </div>

              {/* Expandable Confidence Calculation Breakdown */}
              {showConfidenceDetails && (
                <div className="pt-3 border-t border-zinc-800 space-y-2.5 text-xs text-zinc-300">
                  <div className="p-2.5 rounded-lg bg-black/40 border border-zinc-800/80 font-mono text-[11px] text-zinc-400">
                    <span className="text-zinc-200 font-semibold">Mathematical Basis:</span> {confidence?.mathematical_formula || 'No calibrated confidence formula is claimed in the MVP.'}
                  </div>
                  <p className="text-[11px] text-zinc-400 leading-relaxed italic">
                    {confidence?.calculation_basis || 'Confidence is intentionally not presented as a calibrated probability; inspect the deterministic evidence and stated input limitations instead.'}
                  </p>

                  {/* Factor Breakdown */}
                  {confidence?.provenance_audit && (
                    <div className="space-y-1.5 pt-1">
                      <div className="text-[11px] font-semibold text-zinc-300 uppercase tracking-wider">Consensus Factors:</div>
                      {confidence.provenance_audit.map((f, idx) => (
                        <div key={idx} className="p-2 rounded bg-zinc-900/60 border border-zinc-800/60 flex items-start justify-between gap-2">
                          <div>
                            <div className="font-medium text-zinc-200">{f.factor} <span className="text-[10px] text-zinc-400 font-mono">({f.value})</span></div>
                            <div className="text-[10px] text-zinc-400">{f.scientific_rationale}</div>
                          </div>
                          <span className={`font-mono font-bold text-xs shrink-0 ${f.positive ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {f.weight}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Spatial Resolution & Area Basis */}
            <div className="p-3 rounded-xl bg-zinc-900/40 border border-zinc-800 flex items-center justify-between text-xs text-zinc-400">
              <div className="flex items-center gap-2">
                <Compass className="h-4 w-4 text-purple-400" />
                <span>Resolution Basis: <strong className="text-zinc-200">Pixel grid only (GSD unknown)</strong></span>
              </div>
              <div className="font-mono text-zinc-300">
                {spatialMetrics.total_pixels || results?.measured_metrics?.total_pixels || 'Input'} pixels — physical area unavailable
              </div>
            </div>

            {/* Distribution Bars */}
            {results?.spectral_distribution && (
              <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-2.5">
                <div className="text-xs font-semibold text-zinc-300 flex items-center justify-between">
                  <span>{isRadar ? 'Radar Backscatter Zones' : 'Land-Cover Distribution'}</span>
                  <span className="text-[11px] text-zinc-500 font-mono">100% Normalized</span>
                </div>
                <div className="space-y-2">
                  {Object.entries(results.spectral_distribution).map(([cls, pct]) => (
                    <div key={cls} className="text-xs">
                      <div className="flex justify-between text-zinc-300 mb-1">
                        <span className="truncate pr-2">{cls}</span>
                        <span className="font-mono font-semibold text-zinc-100">{pct}%</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-zinc-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            cls.includes('Water') || cls.includes('River')
                              ? 'bg-cyan-400 shadow-sm shadow-cyan-400/50'
                              : cls.includes('Built-up') || cls.includes('Structural')
                              ? 'bg-amber-400 shadow-sm shadow-amber-400/50'
                              : 'bg-emerald-400 shadow-sm shadow-emerald-400/50'
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: BAND TELEMETRY */}
        {activeTab === 'bands' && (
          <div className="space-y-3">
            <div className="text-xs text-zinc-400">
              Statistical & radiometric engineering telemetry across discrete acquisition channels:
            </div>
            {bandTelemetry.length > 0 ? (
              <div className="overflow-x-auto rounded-xl border border-zinc-800">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-zinc-900/80 border-b border-zinc-800 text-zinc-400">
                      <th className="p-2.5 font-semibold">Band / Channel</th>
                      <th className="p-2.5 font-semibold">Mean</th>
                      <th className="p-2.5 font-semibold">Std Dev</th>
                      <th className="p-2.5 font-semibold">Min-Max</th>
                      <th className="p-2.5 font-semibold">SNR (dB)</th>
                      <th className="p-2.5 font-semibold">Entropy</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60 font-mono">
                    {bandTelemetry.map((b, idx) => (
                      <tr key={idx} className="hover:bg-zinc-900/30 text-zinc-300">
                        <td className="p-2.5 font-sans font-medium text-sky-400">{b.band}</td>
                        <td className="p-2.5 font-semibold text-white">{b.mean}</td>
                        <td className="p-2.5 text-zinc-400">{b.std}</td>
                        <td className="p-2.5 text-zinc-400">[{b.min} - {b.max}]</td>
                        <td className="p-2.5 text-emerald-400 font-semibold">{b.snr_db} dB</td>
                        <td className="p-2.5 text-purple-300">{b.entropy_bits} bits</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-zinc-900/40 border border-zinc-800 text-xs text-zinc-500">
                Band telemetry available on multi-band raster ingestion.
              </div>
            )}

            {/* Geodetic Reference Card */}
            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800 space-y-1.5 text-xs">
              <div className="font-semibold text-zinc-300">Spatial & Geodetic Metadata</div>
              <div className="grid grid-cols-2 gap-2 text-zinc-400 font-mono text-[11px] pt-1">
                <div>CRS: <span className="text-zinc-200">{spatialMetrics.spatial_crs || 'Not provided'}</span></div>
                <div>GSD: <span className="text-zinc-200">{spatialMetrics.ground_sampling_distance_m || 'Unknown'}</span></div>
                <div>Total Pixels: <span className="text-zinc-200">{results?.measured_metrics?.total_pixels?.toLocaleString() || 'Not available'}</span></div>
                <div>Area: <span className="text-zinc-200">Not calculated from image pixels</span></div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: IMAGE PHYSICS & HEURISTICS */}
        {activeTab === 'physics' && (
          <div className="space-y-3">
            {isRadar ? (
              <>
                <div className="text-xs text-zinc-400">
                  Prototype SAR intensity heuristics (not calibrated backscatter):
                </div>
                <div className="grid grid-cols-2 gap-2.5">
                  <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30">
                    <div className="text-[11px] text-cyan-400 font-medium">Low-intensity water-like threshold</div>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">&lt; 42</div>
                    <div className="text-[10px] text-zinc-500 mt-1">8-bit image intensity; not σ⁰</div>
                  </div>
                  <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30">
                    <div className="text-[11px] text-amber-400 font-medium">High-intensity structure-like threshold</div>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">&gt; 140</div>
                    <div className="text-[10px] text-zinc-500 mt-1">8-bit image intensity; prototype heuristic</div>
                  </div>
                </div>

                {eng.hydrological_geometry && (
                  <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800 space-y-2 text-xs">
                    <div className="font-semibold text-zinc-300">Hydrological Corridor Morphology</div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-zinc-400 font-mono text-[11px] pt-1">
                      <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                        <div className="text-zinc-500 text-[10px]">Channel Length</div>
                        <div className="text-white font-bold">{eng.hydrological_geometry.estimated_channel_length_km} km</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                        <div className="text-zinc-500 text-[10px]">Mean Width</div>
                        <div className="text-white font-bold">{eng.hydrological_geometry.mean_channel_width_m} m</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                        <div className="text-zinc-500 text-[10px]">Sinuosity Index</div>
                        <div className="text-white font-bold">{eng.hydrological_geometry.sinuosity_index}</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                        <div className="text-zinc-500 text-[10px]">Equivalent Looks</div>
                        <div className="text-white font-bold">ENL: {eng.equivalent_number_of_looks_enl}</div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <>
                <div className="text-xs text-zinc-400">
                  RGB-based prototype heuristics (not multispectral indices):
                </div>
                {eng.rgb_heuristics && (
                  <div className="grid grid-cols-2 gap-2.5">
                    <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
                      <div className="text-[11px] text-emerald-400 font-medium">Green / Red ratio</div>
                      <div className="text-lg font-bold text-white font-mono mt-0.5">{eng.rgb_heuristics.green_red_ratio}×</div>
                      <div className="text-[10px] text-zinc-500 mt-1">RGB heuristic only</div>
                    </div>
                    <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30">
                      <div className="text-[11px] text-cyan-400 font-medium">Blue / Green ratio</div>
                      <div className="text-lg font-bold text-white font-mono mt-0.5">{eng.rgb_heuristics.blue_green_ratio}×</div>
                      <div className="text-[10px] text-zinc-500 mt-1">RGB heuristic only</div>
                    </div>
                  </div>
                )}

              </>
            )}
          </div>
        )}

        {/* TAB 4: RAW AUDIT MATRIX */}
        {activeTab === 'raw' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-400">Structured JSON provenance payload:</span>
              <button
                onClick={handleCopyJson}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-[11px] text-zinc-300 transition"
              >
                {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
              </button>
            </div>
            <pre className="p-3.5 rounded-xl bg-black/80 border border-zinc-800 text-[11px] font-mono text-zinc-300 max-h-80 overflow-y-auto leading-relaxed">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
