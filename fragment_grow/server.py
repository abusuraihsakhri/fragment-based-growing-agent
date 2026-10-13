"""
FastAPI REST API Server for FragmentGrow: Fragment-Based Drug Discovery (FBDD) Linking & Growing Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import FragmentGrowCoordinator

coordinator = FragmentGrowCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field

        app = FastAPI(
            title="FragmentGrow: Fragment-Based Drug Discovery (FBDD) Linking & Growing Agent",
            description="Legacy heuristic threshold service. Does not compute molecular properties, SAscore, docking or linking vectors.",
            version="2.0.1",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = Field(default=28.5, allow_inf_nan=False)
            secondary_metric: float = Field(default=14.2, allow_inf_nan=False)
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "fragment-based-growing-agent", "domain": "Computational Chemistry & AI Drug Discovery", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
