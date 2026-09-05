import React from 'react';
import { Terminal, CheckCircle2, Cpu, Brain, Layers } from 'lucide-react';

export default function AgentTraceLog({ trace, duration }) {
  if (!trace || trace.length === 0) {
    return (
      <div className="rounded-2xl border border-zinc-800 bg-[#0c0c0e] p-4 flex flex-col items-center justify-center text-zinc-500 h-[220px]">
        <Terminal className="h-6 w-6 stroke-1 mb-2 text-zinc-600" />
        <span className="text-xs">Execution steps and algorithm provenance will stream here during analysis</span>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-zinc-800 bg-[#0c0c0e] overflow-hidden flex flex-col h-[280px] shadow-xl">
      <div className="px-4 py-2.5 border-b border-zinc-800/80 bg-zinc-900/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-sky-400" />
          <span className="text-xs font-semibold text-zinc-200">How This Result Was Produced</span>
          <span className="text-[10px] text-zinc-500 font-mono">({trace.length} pipeline steps)</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Executed in {duration}ms</span>
        </div>
      </div>

      <div className="p-3 font-mono text-[11px] overflow-y-auto space-y-2.5 flex-1 select-text">
        {trace.map((step) => {
          let badgeColor = 'text-zinc-400 border-zinc-800 bg-zinc-900';
          if (step.stage === 'INTENT_PLAN' || step.stage === 'CLASSIFY') badgeColor = 'text-purple-300 border-purple-500/30 bg-purple-500/10';
          if (step.stage === 'VALIDATE') badgeColor = 'text-amber-300 border-amber-500/30 bg-amber-500/10';
          if (step.stage === 'DISPATCH' || step.stage === 'COMPUTE') badgeColor = 'text-sky-300 border-sky-500/30 bg-sky-500/10';
          if (step.stage === 'CONFIDENCE') badgeColor = 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10';
          if (step.stage === 'REPORT') badgeColor = 'text-pink-300 border-pink-500/30 bg-pink-500/10';

          const subsystem = step.details?.subsystem;
          const isAI = subsystem?.includes('AI Agent') || subsystem?.includes('Intent');
          const isRS = subsystem?.includes('Classical RS') || subsystem?.includes('Algorithm');

          return (
            <div key={step.step_id} className="p-2 rounded-lg bg-zinc-900/40 border border-zinc-800/60 space-y-1">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-zinc-500 text-[10px]">+{step.timestamp_ms}ms</span>
                  <span className={`px-1.5 py-0.5 rounded border text-[9px] font-bold tracking-wider shrink-0 ${badgeColor}`}>
                    {step.stage}
                  </span>
                </div>
                {subsystem && (
                  <span className={`text-[10px] font-sans px-2 py-0.5 rounded-full border flex items-center gap-1 ${
                    isAI 
                      ? 'bg-purple-950/40 text-purple-300 border-purple-500/30' 
                      : isRS 
                      ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30'
                      : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                  }`}>
                    {isAI ? <Brain className="h-2.5 w-2.5 text-purple-400" /> : isRS ? <Cpu className="h-2.5 w-2.5 text-emerald-400" /> : <Layers className="h-2.5 w-2.5 text-zinc-400" />}
                    <span>{subsystem}</span>
                  </span>
                )}
              </div>
              <p className="text-zinc-200 text-xs leading-relaxed font-sans">{step.message}</p>
              {step.details?.derivation && (
                <p className="text-[10px] text-zinc-400 italic font-mono pt-0.5">
                  &rarr; {step.details.derivation}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
