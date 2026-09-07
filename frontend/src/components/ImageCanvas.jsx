import React, { useState } from 'react';
import { 
  Layers, 
  Eye, 
  Sliders, 
  SplitSquareHorizontal, 
  MapPin, 
  Calendar, 
  ShieldCheck,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function ImageCanvas({ result }) {
  const [sliderPos, setSliderPos] = useState(50);
  const [activeLayer, setActiveLayer] = useState('overlay'); // 'overlay' | 'raw' | 'split'
  const [fusionMode, setFusionMode] = useState('overlay'); // 'optical' | 'sar' | 'overlay'

  if (!result || !result.results) {
    return (
      <div className="h-[460px] rounded-2xl border border-dashed border-zinc-800 bg-zinc-950/30 flex flex-col items-center justify-center text-zinc-500">
        <Layers className="h-10 w-10 stroke-1 mb-2 text-zinc-600 animate-pulse" />
        <p className="text-sm font-medium text-zinc-400">Select an SIH Scenario or upload satellite imagery to begin</p>
        <span className="text-xs text-zinc-600 mt-1">Supports Sentinel-1 C-SAR &middot; Sentinel-2 MSI Multi-Band &middot; GeoTIFF</span>
      </div>
    );
  }

  const { task, results, provenance, modalities } = result;
  const isTemporal = task === 'TEMPORAL_CHANGE' || task === 'CHANGE_VQA';
  const isFusion = task === 'OPTICAL_SAR_FUSION';
  const isGrounding = task === 'GROUNDING';
  const isRadar = modalities?.[0]?.is_radar || results?.measured_metrics?.is_radar;
  const isCloudRefusal = results?.insufficient_evidence;

  const rawUrl = results.raw_image_url || results.t1_url || results.optical_url;
  const maskUrl = results.overlay_url || results.annotated_url || results.change_heatmap_url || results.fused_url;

  return (
    <div className="rounded-2xl border border-zinc-800 bg-[#0c0c0e] overflow-hidden flex flex-col shadow-xl">
      {/* Top Canvas Toolbar */}
      <div className="px-4 py-3 border-b border-zinc-800/80 bg-zinc-900/50 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-zinc-100 uppercase tracking-wide">Interactive Canvas</span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 font-mono">
            {task}
          </span>
          {isCloudRefusal && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/20 border border-rose-500/30 text-rose-300 font-semibold flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              REFUSAL BENCHMARK
            </span>
          )}
        </div>

        {/* 3-Way Mode Switcher (Raw vs Mask vs Split) */}
        {!isTemporal && !isFusion && (
          <div className="flex items-center gap-1 bg-zinc-900 p-1 rounded-xl border border-zinc-800 self-start sm:self-auto">
            <button
              onClick={() => setActiveLayer('raw')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                activeLayer === 'raw'
                  ? 'bg-zinc-800 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              Raw Satellite Raster
            </button>
            <button
              onClick={() => setActiveLayer('overlay')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                activeLayer === 'overlay'
                  ? 'bg-sky-500 text-black font-semibold shadow-sm shadow-sky-500/20'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              Analytical Mask
            </button>
            <button
              onClick={() => setActiveLayer('split')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition flex items-center gap-1 ${
                activeLayer === 'split'
                  ? 'bg-zinc-800 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <SplitSquareHorizontal className="h-3.5 w-3.5" />
              <span>Split Swipe</span>
            </button>
          </div>
        )}

        {/* Fusion 3-Way Switcher */}
        {isFusion && (
          <div className="flex items-center gap-1 bg-zinc-900 p-1 rounded-xl border border-zinc-800">
            <button
              onClick={() => setFusionMode('optical')}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                fusionMode === 'optical' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
              }`}
            >
              Optical (VNIR)
            </button>
            <button
              onClick={() => setFusionMode('sar')}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                fusionMode === 'sar' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
              }`}
            >
              SAR Radar
            </button>
            <button
              onClick={() => setFusionMode('overlay')}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                fusionMode === 'overlay' ? 'bg-sky-500 text-black' : 'text-zinc-400 hover:text-white'
              }`}
            >
              Fused Output
            </button>
          </div>
        )}

        {/* Temporal Swipe Indicator */}
        {isTemporal && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-sky-400">
            <SplitSquareHorizontal className="h-3.5 w-3.5" />
            <span className="text-[11px] text-zinc-300 font-mono">Bi-Temporal Swipe Active</span>
          </div>
        )}
      </div>

      {/* Geospatial Provenance Metadata Bar */}
      {provenance && (
        <div className="px-4 py-2 bg-zinc-950/80 border-b border-zinc-800/60 flex flex-wrap items-center justify-between gap-3 text-[11px] text-zinc-400">
          <div className="flex items-center gap-2">
            <span className="px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 font-semibold border border-sky-500/20">
              {provenance.platform || 'Sentinel-2A'}
            </span>
            <span className="text-zinc-300">{provenance.product_level || 'Level-2A BOA'}</span>
          </div>
          {provenance.location && (
            <div className="flex items-center gap-1 text-zinc-300">
              <MapPin className="h-3.5 w-3.5 text-rose-400" />
              <span>{provenance.location}</span>
            </div>
          )}
          {provenance.acquisition_date && (
            <div className="flex items-center gap-1 text-zinc-400">
              <Calendar className="h-3.5 w-3.5 text-zinc-500" />
              <span>{provenance.acquisition_date}</span>
            </div>
          )}
          <div className="font-mono text-zinc-400">
            GSD: <strong className="text-zinc-200">{provenance.gsd || '10.0 m/px'}</strong>
          </div>
        </div>
      )}

      {/* Primary Canvas Viewport */}
      <div className="relative h-[440px] w-full flex items-center justify-center bg-black/60 overflow-hidden select-none">
        {/* Temporal Split-Slider View */}
        {isTemporal && results.t1_url && results.change_heatmap_url ? (
          <div className="relative w-full h-full max-w-[512px] max-h-[440px] mx-auto overflow-hidden">
            {/* T1 Baseline */}
            <img
              src={results.t1_url}
              alt="T1 Baseline"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />
            {/* T2 Change Heatmap */}
            <div
              className="absolute inset-0 overflow-hidden pointer-events-none"
              style={{ clipPath: `polygon(${sliderPos}% 0, 100% 0, 100% 100%, ${sliderPos}% 100%)` }}
            >
              <img
                src={results.change_heatmap_url}
                alt="Change Heatmap"
                className="w-full h-full object-contain"
              />
            </div>
            {/* Split Divider */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-sky-400 shadow-xl cursor-ew-resize z-20"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-7 w-7 rounded-full bg-sky-500 border-2 border-white flex items-center justify-center text-[10px] text-white font-bold shadow-lg">
                ⇄
              </div>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-30"
            />
            <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur px-2.5 py-1 rounded text-[11px] font-mono text-zinc-300 border border-white/10 z-10">
              T1 (Baseline Acquisition)
            </div>
            <div className="absolute bottom-3 right-3 bg-black/80 backdrop-blur px-2.5 py-1 rounded text-[11px] font-mono text-sky-400 border border-sky-500/30 z-10">
              T2 (Differential Change Heatmap)
            </div>
          </div>
        ) : isFusion ? (
          /* Fusion Multi-Layer View */
          <div className="relative w-full h-full max-w-[512px] max-h-[440px] mx-auto flex items-center justify-center">
            <img
              src={
                fusionMode === 'optical'
                  ? results.optical_url
                  : fusionMode === 'sar'
                  ? results.sar_url
                  : results.fused_url
              }
              alt="Fusion Scene"
              className="w-full h-full object-contain transition-all duration-200"
            />
            <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur px-2.5 py-1 rounded text-[11px] font-mono text-zinc-300 border border-white/10">
              Active Layer: <span className="text-sky-400 font-semibold uppercase">{fusionMode}</span>
            </div>
          </div>
        ) : activeLayer === 'split' && rawUrl && maskUrl ? (
          /* Split View for Single Scenes */
          <div className="relative w-full h-full max-w-[512px] max-h-[440px] mx-auto overflow-hidden">
            <img
              src={rawUrl}
              alt="Raw Raster"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />
            <div
              className="absolute inset-0 overflow-hidden pointer-events-none"
              style={{ clipPath: `polygon(${sliderPos}% 0, 100% 0, 100% 100%, ${sliderPos}% 100%)` }}
            >
              <img
                src={maskUrl}
                alt="Analytical Mask"
                className="w-full h-full object-contain"
              />
            </div>
            <div
              className="absolute top-0 bottom-0 w-1 bg-sky-400 shadow-xl cursor-ew-resize z-20"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-7 w-7 rounded-full bg-sky-500 border-2 border-white flex items-center justify-center text-[10px] text-white font-bold shadow-lg">
                ⇄
              </div>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-30"
            />
            <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur px-2.5 py-1 rounded text-[11px] font-mono text-zinc-300 border border-white/10 z-10">
              Raw Satellite Raster
            </div>
            <div className="absolute bottom-3 right-3 bg-black/80 backdrop-blur px-2.5 py-1 rounded text-[11px] font-mono text-sky-400 border border-sky-500/30 z-10">
              Classified Mask Overlay
            </div>
          </div>
        ) : (
          /* Standard Single Layer View */
          <div className="relative w-full h-full max-w-[512px] max-h-[440px] mx-auto flex items-center justify-center">
            <img
              src={activeLayer === 'raw' && rawUrl ? rawUrl : maskUrl || rawUrl}
              alt="Scene Output"
              className="w-full h-full object-contain"
            />
            <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur px-2.5 py-1 rounded text-[11px] font-mono text-zinc-300 border border-white/10">
              View: <span className="text-sky-400 font-semibold">{activeLayer === 'raw' ? 'Raw Satellite Raster' : 'Analytical Mask Overlay'}</span>
            </div>
          </div>
        )}

        {/* Map Legend Overlay */}
        <div className="absolute top-3 right-3 bg-black/85 backdrop-blur-md p-2.5 rounded-xl border border-zinc-800 text-[11px] space-y-1.5 shadow-2xl z-10 max-w-[200px]">
          <div className="font-semibold text-zinc-300 text-[10px] uppercase tracking-wider border-b border-zinc-800 pb-1">
            Map Legend
          </div>
          {isRadar ? (
            <div className="space-y-1 text-zinc-300">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-cyan-400 shadow-sm shrink-0" />
                <span className="truncate">Water (Specular)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-amber-400 shadow-sm shrink-0" />
                <span className="truncate">Structures (Corner)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-zinc-400 shadow-sm shrink-0" />
                <span className="truncate">Terrain (Diffuse)</span>
              </div>
            </div>
          ) : isCloudRefusal ? (
            <div className="space-y-1 text-zinc-300">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-rose-500 shadow-sm shrink-0" />
                <span className="truncate">Tropospheric Clouds</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-zinc-600 shadow-sm shrink-0" />
                <span className="truncate">Obscured Terrain</span>
              </div>
            </div>
          ) : (
            <div className="space-y-1 text-zinc-300">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-cyan-400 shadow-sm shrink-0" />
                <span className="truncate">Water / River</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-emerald-400 shadow-sm shrink-0" />
                <span className="truncate">Canopy / Vegetation</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-lime-400 shadow-sm shrink-0" />
                <span className="truncate">Agricultural Fields</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-amber-400 shadow-sm shrink-0" />
                <span className="truncate">Built-up / Urban</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
