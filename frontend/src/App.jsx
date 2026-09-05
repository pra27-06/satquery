import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Sparkles, Send, UploadCloud, Loader2, Layers, BookmarkCheck } from 'lucide-react';

import Header from './components/Header';
import SmartIngestStudio from './components/SmartIngestStudio';
import DemoPresetBar from './components/DemoPresetBar';
import ImageCanvas from './components/ImageCanvas';
import AgentTraceLog from './components/AgentTraceLog';
import ResultInspector from './components/ResultInspector';
import UploadModal from './components/UploadModal';
import Footer from './components/Footer';

import { fetchHealth, fetchDemos, runDemoScenario, analyzeCustomQuery } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('studio'); // 'studio' | 'presets'
  const [activeDemoId, setActiveDemoId] = useState('demo-sar');
  const [customQuery, setCustomQuery] = useState('');
  const [currentResult, setCurrentResult] = useState(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isStudioCollapsed, setIsStudioCollapsed] = useState(false);

  // Queries
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: fetchHealth });
  const { data: demosData } = useQuery({ queryKey: ['demos'], queryFn: fetchDemos });

  const demos = demosData?.demos || [];

  // Mutation for running preset demo
  const demoMutation = useMutation({
    mutationFn: runDemoScenario,
    onSuccess: (data) => {
      setCurrentResult(data);
      setIsStudioCollapsed(true);
    },
  });

  // Mutation for custom analysis
  const customMutation = useMutation({
    mutationFn: ({ query, files }) => analyzeCustomQuery(query, files),
    onSuccess: (data) => {
      setCurrentResult(data);
      setIsStudioCollapsed(true);
    },
  });

  const isLoading = demoMutation.isPending || customMutation.isPending;

  // Auto-run Demo SAR on initial load so the user immediately sees the river SAR detection!
  useEffect(() => {
    if (demos.length > 0 && !currentResult && !demoMutation.isPending) {
      demoMutation.mutate('demo-sar');
    }
  }, [demos.length]);

  const handleSelectDemo = (demoId) => {
    setActiveDemoId(demoId);
    demoMutation.mutate(demoId);
  };

  const handlePresetQuerySubmit = (e) => {
    e.preventDefault();
    if (!customQuery.trim()) return;
    if (activeDemoId) {
      demoMutation.mutate(activeDemoId);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 flex flex-col font-sans antialiased selection:bg-sky-500/20 selection:text-sky-300">
      <Header health={health} />

      {/* Main Expansive Container with Ergonomic PC Spacing */}
      <main className="flex-1 max-w-[1550px] w-full mx-auto px-4 sm:px-6 lg:px-10 py-6 space-y-6">
        {/* Navigation Mode Switcher */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-zinc-800/80 pb-4">
          <div className="flex items-center gap-2 p-1 rounded-xl bg-zinc-900/90 border border-zinc-800 shadow-inner">
            <button
              onClick={() => setActiveTab('studio')}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'studio'
                  ? 'bg-sky-500 text-black shadow-md shadow-sky-500/20'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
              }`}
            >
              <Layers className="h-4 w-4" />
              <span>Smart Ingestion Studio</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] bg-cyan-400/20 text-cyan-900 font-bold tracking-wide">
                AUTO-DETECT
              </span>
            </button>

            <button
              onClick={() => setActiveTab('presets')}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'presets'
                  ? 'bg-sky-500 text-black shadow-md shadow-sky-500/20'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
              }`}
            >
              <BookmarkCheck className="h-4 w-4" />
              <span>1-Click SIH Benchmarks (7 Scenarios)</span>
            </button>
          </div>

          <div className="text-xs text-zinc-400 flex items-center gap-2.5 bg-zinc-900/60 px-3 py-1.5 rounded-lg border border-zinc-800">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-medium text-zinc-300">Dual Sensor Core: Sentinel-1 C-SAR &middot; Sentinel-2 MSI Optical</span>
          </div>
        </div>

        {/* Tab 1: Smart Ingestion Studio (Contains integrated query input & execution) */}
        {activeTab === 'studio' && (
          <SmartIngestStudio
            onAnalyze={(query, files) => customMutation.mutate({ query, files })}
            isLoading={isLoading}
            isCollapsed={isStudioCollapsed && !!currentResult}
            onToggleCollapse={() => setIsStudioCollapsed(!isStudioCollapsed)}
          />
        )}

        {/* Tab 2: 1-Click SIH Presets */}
        {activeTab === 'presets' && (
          <div className="space-y-4">
            <DemoPresetBar
              demos={demos}
              activeDemoId={activeDemoId}
              onSelectDemo={handleSelectDemo}
              isLoading={isLoading}
            />

            {/* Inline Query Bar exclusively for Presets mode */}
            <div className="bg-[#111115] border border-zinc-800 p-2.5 rounded-2xl flex items-center gap-3 shadow-xl">
              <div className="pl-3 text-sky-400">
                <Sparkles className="h-4 w-4" />
              </div>
              <input
                type="text"
                placeholder={
                  currentResult?.query
                    ? `Preset query: "${currentResult.query}" (type to customize question on this scenario)`
                    : "Ask a custom question about this scenario image..."
                }
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
                className="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none px-2"
              />
              <button
                onClick={() => setIsUploadOpen(true)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-xs font-medium text-zinc-300 transition"
              >
                <UploadCloud className="h-4 w-4 text-zinc-400" />
                <span className="hidden sm:inline">Upload Files</span>
              </button>
              <button
                onClick={handlePresetQuerySubmit}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-black text-xs font-semibold shadow-md shadow-sky-500/20 transition disabled:opacity-50"
              >
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                <span>Execute</span>
              </button>
            </div>
          </div>
        )}

        {/* Loading Banner */}
        {isLoading && (
          <div className="p-3.5 rounded-xl bg-sky-950/20 border border-sky-500/30 flex items-center gap-3 text-sky-300 text-xs animate-pulse shadow-lg">
            <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
            <span className="font-medium">Agentic Orchestrator Active: Validating rasters, diagnosing sensor physics, and extracting spatial evidence...</span>
          </div>
        )}

        {/* Primary Split View: Canvas on Left, Deep Engineering Inspector on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
          {/* Left Column: Interactive Image Canvas & Agent Trace (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            <ImageCanvas result={currentResult} />
            <AgentTraceLog
              trace={currentResult?.trace || []}
              duration={currentResult?.duration_ms || 0}
            />
          </div>

          {/* Right Column: Multi-Tab Deep Engineering Inspector (5 cols) */}
          <div className="lg:col-span-5 space-y-6 sticky top-6">
            <ResultInspector result={currentResult} />
          </div>
        </div>
      </main>

      {/* Upload Modal (fallback) */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onSubmit={(query, files) => customMutation.mutate({ query, files })}
        isLoading={customMutation.isPending}
      />

      {/* Copyright Footer */}
      <Footer />
    </div>
  );
}
