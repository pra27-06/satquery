import React from 'react';
import { Play, Sparkles } from 'lucide-react';

export default function DemoPresetBar({ demos, activeDemoId, onSelectDemo, isLoading }) {
  return (
    <div className="border-b border-zinc-800/80 bg-zinc-950/40 px-6 py-2.5">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="h-3.5 w-3.5 text-sky-400" />
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Official SIH Evaluation Scenarios (1-Click Presets)
        </span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {demos.map((d) => {
          const isActive = activeDemoId === d.id;
          return (
            <button
              key={d.id}
              onClick={() => onSelectDemo(d.id)}
              disabled={isLoading}
              className={`text-left p-2.5 rounded-lg border transition-all duration-150 flex flex-col justify-between ${
                isActive
                  ? 'bg-sky-950/30 border-sky-500/50 text-white shadow-sm shadow-sky-500/10'
                  : 'bg-zinc-900/60 border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900 text-zinc-300'
              }`}
            >
              <div className="flex items-center justify-between gap-1 w-full mb-1">
                <span className="text-[11px] font-bold text-sky-400 uppercase tracking-tight">
                  {d.tag}
                </span>
                <Play className={`h-3 w-3 ${isActive ? 'text-sky-400 fill-sky-400' : 'text-zinc-500'}`} />
              </div>
              <div className="text-xs font-medium truncate">{d.title.split(':')[1] || d.title}</div>
              <div className="text-[10px] text-zinc-500 truncate mt-0.5">{d.modality}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
