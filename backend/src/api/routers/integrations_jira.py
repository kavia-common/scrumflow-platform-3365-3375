from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..dependencies import get_session
from ..repositories import TaskRepository
from ..services.jira_service import JiraService
from ..config import get_jira_config

router = APIRouter(
    prefix="/integrations/jira",
    tags=["Integrations - Jira"],
)


# PUBLIC_INTERFACE
@router.get(
    "/readiness",
    summary="Jira integration readiness",
    description=(
        "Returns whether Jira MCP integration is enabled based on "
        "environment configuration."
    ),
)
def jira_readiness():
    """
    Jira integration readiness endpoint.

    Returns:
        dict: {
            "enabled": bool indicating if all required Jira MCP env vars are present,
            "missing": list of missing environment variable names
        }
    """
    cfg = get_jira_config()
    return {
        "enabled": bool(cfg.enabled),
        "missing": [
            name
            for name, value in [
                ("JIRA_BASE_URL", cfg.base_url),
                ("JIRA_EMAIL", cfg.email),
                ("JIRA_API_TOKEN", cfg.api_token),
                ("JIRA_PROJECT_KEY", cfg.project_key),
                ("MCP_CLIENT_CMD", cfg.mcp_client_cmd),
            ]
            if not value
        ],
    }


class CreateJiraIssuePayload(BaseModel):
    task_id: int = Field(
        ...,
        description="Task id to link and create a corresponding Jira issue",
    )
    summary: str = Field(..., description="Jira issue summary")
    description: str = Field("", description="Jira issue description")
    issue_type: str = Field("Task", description="Jira issue type")


class TransitionIssuePayload(BaseModel):
    status_name: str = Field(
        ...,
        description="Target Jira status name (e.g., 'In Progress', 'Done')",
    )


# PUBLIC_INTERFACE
@router.post(
    "/issues",
    summary="Create and link a Jira issue for a task",
    description=(
        "Creates a Jira issue via MCP and persists the returned issue key to "
        "the task's jira_issue_key field."
    ),
)
def create_linked_issue(payload: CreateJiraIssuePayload, session: Session = Depends(get_session)):
    """
    Create a Jira issue via MCP and link it to a task.

    Args:
        payload (CreateJiraIssuePayload): Contains task_id, summary, description, and issue_type.
        session (Session): Database session (FastAPI dependency).

    Returns:
        dict: { "task_id": int, "jira_issue_key": str }

    Raises:
        HTTPException: 404 if task not found; 503 if integration not configured; 502 on MCP failure;
                       500 if persistence of jira_issue_key fails.
    """
    repo = TaskRepository(session)
    t = repo.get(payload.task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    cfg = get_jira_config()
    if not cfg.enabled:
        raise HTTPException(status_code=503, detail="Jira integration not configured")

    jira = JiraService()
    key = jira.create_issue(
        project_key=cfg.project_key or "",
        summary=payload.summary,
        description=payload.description or "",
        issue_type=payload.issue_type or "Task",
    )
    if not key:
        raise HTTPException(status_code=502, detail="Failed to create Jira issue via MCP")

    # Persist linkage using TaskUpdate model
    from ..models import TaskUpdate  # local import to avoid circulars at module import time
    updated = repo.update(t.id, data=TaskUpdate(jira_issue_key=key))
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to persist Jira linkage")

    return {"task_id": updated.id, "jira_issue_key": key}


# PUBLIC_INTERFACE
@router.post(
    "/issues/{issue_key}/transition",
    summary="Transition a Jira issue",
    description="Transitions a Jira issue to the provided status name via MCP.",
)
def transition_issue(issue_key: str, payload: TransitionIssuePayload):
    """
    Transition a Jira issue to a target status via MCP.

    Args:
        issue_key (str): Jira issue key (e.g., PROJ-123)
        payload (TransitionIssuePayload): Contains status_name, the target Jira workflow status.

    Returns:
        dict: { "issue_key": str, "status": str, "ok": True }

    Raises:
        HTTPException: 503 if integration not configured; 502 if transition fails.
    """
    cfg = get_jira_config()
    if not cfg.enabled:
        raise HTTPException(status_code=503, detail="Jira integration not configured")
    jira = JiraService()
    ok = jira.transition_issue(issue_key=issue_key, status_name=payload.status_name)
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to transition issue")
    return {"issue_key": issue_key, "status": payload.status_name, "ok": True}
