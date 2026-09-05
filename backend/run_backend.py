"""
run_backend.py
--------------
Starts the SatQuery AI FastAPI backend server.
Optimized to run smoothly without recursive file watcher overhead.
"""

import os
import sys
from pathlib import Path
import uvicorn

# Ensure satquery-ai root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting SatQuery AI Backend on http://0.0.0.0:{port} ...")
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Avoid traversing node_modules and .venv on disk
        workers=1,
        log_level="info"
    )
