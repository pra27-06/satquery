import React from 'react';
import { Satellite, ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-zinc-800/80 bg-[#09090b] px-6 py-4 mt-auto text-xs text-zinc-500 flex flex-col sm:flex-row items-center justify-between gap-2">
      <div className="flex items-center gap-2">
        <Satellite className="h-3.5 w-3.5 text-sky-400" />
        <span className="text-zinc-400 font-medium">SatQuery AI</span>
        <span>·</span>
        <span>SIH 2026 Problem Statement SIH26167 (ISRO)</span>
      </div>
      <div className="flex items-center gap-2 text-zinc-400">
        <span>© 2026 SatQuery AI. All rights reserved.</span>
      </div>
    </footer>
  );
}
