"""
report.py
---------
Evidence report retrieval and export API route.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

# In-memory store for session reports
REPORT_STORE = {}

def store_report(session_id: str, html: str, data: dict):
    REPORT_STORE[session_id] = {"html": html, "data": data}

@router.get("/report/{session_id}")
async def get_report_html(session_id: str):
    if session_id not in REPORT_STORE:
        raise HTTPException(status_code=404, detail="Report not found for session.")
    return HTMLResponse(content=REPORT_STORE[session_id]["html"])

@router.get("/report/{session_id}/json")
async def get_report_json(session_id: str):
    if session_id not in REPORT_STORE:
        raise HTTPException(status_code=404, detail="Report not found for session.")
    return REPORT_STORE[session_id]["data"]
