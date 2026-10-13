"""
FastAPI REST API Server for Fragment Based Growing Agent.
"""
from typing import Dict, Any, List, Optional
import os
import hmac
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .metrics import GLOBAL_METRICS
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Fragment Based Growing Agent API",
    description="Enterprise Distributed Component Platform (AI Drug Discovery, Structural Biology & Wet-Lab Robotics)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "fragment-based-growing-agent", "domain": "AI Drug Discovery, Structural Biology & Wet-Lab Robotics", "standard": "wwPDB / IUPAC / OpenSMILES / ISAC Standards", "version": "3.0.0-ENTERPRISE"}


@app.exception_handler(SecurityException)
async def reject_sensitive_input(request, exc):
    return JSONResponse(status_code=422, content={"detail": "Potential sensitive identifier detected."})


@app.get("/metrics")
def metrics():
    return PlainTextResponse(GLOBAL_METRICS.export_prometheus_text(), media_type="text/plain; version=0.0.4")


@app.get("/api/metrics")
def metrics_json():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL",
    }

@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Potential sensitive identifier detected.")


@app.get("/api/audit/logs")
def api_audit_logs(authorization: Optional[str] = Header(default=None)):
    """Expose operational audit metadata only when explicitly configured."""
    expected = os.getenv("AUDIT_LOGS_TOKEN")
    supplied = authorization[7:] if authorization and authorization.startswith("Bearer ") else ""
    if not expected or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=403, detail="Audit logs access denied")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
