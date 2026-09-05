import React from 'react';
import { Satellite, ShieldCheck, Cpu, ExternalLink } from 'lucide-react';

export default function Header({ health }) {
  return (
    <header className="border-b border-zinc-800 bg-[#09090b]/80 backdrop-blur sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
          <Satellite className="h-5 w-5 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-semibold tracking-tight text-white">
              SatQuery <span className="text-sky-400">AI</span>
            </h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-300">
              SIH26167 · ISRO
            </span>
          </div>
          <p className="text-xs text-zinc-400">
            Interactive Multimodal Remote Sensing Intelligence Platform
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300">
          <Cpu className="h-3.5 w-3.5 text-sky-400" />
          <span>Core: <span className="text-white font-mono">Neuro-Symbolic (LLM Agent + RS Physics)</span></span>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping"></span>
          <span>{health?.status === 'HEALTHY' ? 'Online' : 'Connected'}</span>
        </div>
      </div>
    </header>
  );
}
