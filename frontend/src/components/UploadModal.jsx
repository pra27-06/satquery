import React, { useState } from 'react';
import { Upload, X, ArrowRight } from 'lucide-react';

export default function UploadModal({ isOpen, onClose, onSubmit, isLoading }) {
  const [query, setQuery] = useState('');
  const [files, setFiles] = useState([]);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (files.length === 0 || !query.trim()) return;
    onSubmit(query, files);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0f0f12] border border-zinc-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
          <h3 className="text-base font-semibold text-white">Upload Custom Satellite Imagery</h3>
          <button onClick={onClose} className="text-zinc-400 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-1.5">
              Select Satellite Raster Files (GeoTIFF / TIFF / PNG / JPG)
            </label>
            <div className="border-2 border-dashed border-zinc-700 hover:border-sky-500/50 rounded-xl p-6 text-center cursor-pointer bg-zinc-900/30">
              <Upload className="h-8 w-8 mx-auto text-zinc-500 mb-2" />
              <input
                type="file"
                multiple
                accept=".tif,.tiff,.png,.jpg,.jpeg"
                onChange={handleFileChange}
                className="block w-full text-xs text-zinc-400 file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-sky-500/10 file:text-sky-400 hover:file:bg-sky-500/20"
              />
              <p className="text-[11px] text-zinc-500 mt-2">
                Upload 1 image for VQA/Grounding, or 2 images for Temporal Change / Optical+SAR
              </p>
            </div>
            {files.length > 0 && (
              <div className="mt-2 text-xs text-emerald-400">
                Selected {files.length} file(s): {files.map((f) => f.name).join(', ')}
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-1.5">
              Natural Language Query
            </label>
            <input
              type="text"
              placeholder="e.g. Highlight the water bodies or Describe what changed between these dates"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 text-xs font-medium hover:bg-zinc-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || files.length === 0 || !query.trim()}
              className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-black text-xs font-semibold flex items-center gap-1.5 disabled:opacity-50"
            >
              <span>Execute Agent</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
