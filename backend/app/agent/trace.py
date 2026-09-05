"""
trace.py
--------
Execution trace logger for recording agentic steps, decisions,
sub-tool parameters, and timestamps for judge auditing.
"""

import time
from typing import List, Dict, Any

class AgentTrace:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    def add_step(self, stage: str, message: str, details: Dict[str, Any] = None):
        elapsed = round((time.time() - self.start_time) * 1000, 2)
        step = {
            "step_id": len(self.steps) + 1,
            "timestamp_ms": elapsed,
            "stage": stage,
            "message": message,
            "details": details or {}
        }
        self.steps.append(step)
        
    def get_trace_log(self) -> List[Dict[str, Any]]:
        return self.steps
        
    def total_duration_ms(self) -> float:
        return round((time.time() - self.start_time) * 1000, 2)
