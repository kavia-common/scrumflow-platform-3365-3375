from __future__ import annotations

import json
import logging
import subprocess
from typing import Any, Optional

from ..config import get_jira_config

logger = logging.getLogger(__name__)


class JiraService:
    """
    Service wrapper that talks to an MCP client process exposing Jira tools.

    The MCP client command is provided via env (MCP_CLIENT_CMD) and is executed per call
    with a JSON payload describing the tool to run and its arguments.

    All calls are resilient: if configuration is missing or execution fails, we log and return None/False.
    """

    def __init__(self) -> None:
        self.cfg = get_jira_config()

    def _is_enabled(self) -> bool:
        return self.cfg.enabled

    def _run_tool(self, tool_name: str, args: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Execute the MCP client with a JSON payload containing the tool name and args.

        Expected convention for the MCP client: read JSON on stdin and output JSON on stdout
        containing at minimum a 'success' boolean and optionally 'data' or 'error'.
        """
        if not self._is_enabled():
            logger.info("Jira MCP disabled: missing configuration; tool=%s skipped", tool_name)
            return None

        payload = {
            "tool": tool_name,
            "args": args,
            # Provide Jira auth/context so client can call Jira Cloud
            "context": {
                "base_url": self.cfg.base_url,
                "email": self.cfg.email,
                "api_token": self.cfg.api_token,
            },
        }

        try:
            cmd = self.cfg.mcp_client_cmd or ""
            if not cmd:
                logger.warning("MCP client command not configured; skipping Jira call: %s", tool_name)
                return None

            # Use shell tokenization for safety, but we run shell=True only when necessary.
            # Here we pass string to shell to allow complex commands, documented by env.
            completed = subprocess.run(
                cmd,  # type: ignore[arg-type]
                input=json.dumps(payload).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                check=False,
            )

            if completed.returncode != 0:
                logger.error("MCP client returned non-zero exit status: %s, stderr=%s",
                             completed.returncode, completed.stderr.decode("utf-8", errors="ignore"))
                return None

            raw = completed.stdout.decode("utf-8", errors="ignore").strip()
            if not raw:
                logger.error("MCP client returned empty output for tool=%s", tool_name)
                return None

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                logger.exception("Failed to decode MCP client JSON output: %s", raw[:1000])
                return None

            return data if isinstance(data, dict) else None

        except Exception:
            logger.exception("Exception while invoking MCP client for tool=%s", tool_name)
            return None

    # PUBLIC_INTERFACE
    def create_issue(self, *, project_key: str, summary: str, description: str,
                     issue_type: str = "Task") -> Optional[str]:
        """Create a Jira issue and return its key (e.g., PROJ-123) or None on failure."""
        resp = self._run_tool(
            "createIssue",
            {
                "projectKey": project_key,
                "summary": summary,
                "description": description,
                "issueType": issue_type,
            },
        )
        if not resp:
            return None
        if resp.get("success") and isinstance(resp.get("data"), dict):
            return resp["data"].get("key")
        logger.warning("createIssue did not succeed; resp=%s", resp)
        return None

    # PUBLIC_INTERFACE
    def transition_issue(self, *, issue_key: str, status_name: str) -> bool:
        """Transition a Jira issue to the given workflow status name. Returns True if success."""
        resp = self._run_tool(
            "transitionIssue",
            {
                "issueKey": issue_key,
                "statusName": status_name,
            },
        )
        if not resp:
            return False
        ok = bool(resp.get("success"))
        if not ok:
            logger.warning("transitionIssue failed for %s -> %s; resp=%s", issue_key, status_name, resp)
        return ok

    # PUBLIC_INTERFACE
    def add_comment(self, *, issue_key: str, comment: str) -> bool:
        """Add a comment to a Jira issue. Returns True on success."""
        resp = self._run_tool(
            "addComment",
            {
                "issueKey": issue_key,
                "comment": comment,
            },
        )
        if not resp:
            return False
        ok = bool(resp.get("success"))
        if not ok:
            logger.warning("addComment failed for %s; resp=%s", issue_key, resp)
        return ok


# Helper to map internal statuses to Jira workflow names
STATUS_TO_JIRA = {
    "todo": "To Do",
    "in_progress": "In Progress",
    "done": "Done",
    "blocked": "Blocked",
}


# PUBLIC_INTERFACE
def map_task_status_to_jira(status: str) -> str:
    """Map internal TaskStatus string to a Jira workflow status name."""
    return STATUS_TO_JIRA.get(status, status.title())
