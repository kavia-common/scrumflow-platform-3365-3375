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
        """Initialize JiraService by loading Jira MCP configuration from environment."""
        self.cfg = get_jira_config()

    def _is_enabled(self) -> bool:
        """Return True if Jira MCP integration is fully enabled/configured."""
        return self.cfg.enabled

    def _run_tool(self, tool_name: str, args: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Execute the MCP client with a JSON payload containing the tool name and args.

        Expected MCP client convention:
        - Read a single JSON object on stdin: {"tool": "<name>", "args": {...}, "context": {...}}
        - Write a single JSON object on stdout: {"success": true/false, "data": {...}? , "error": "..."}.
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

            # Use shell to support multi-word commands (e.g., "mcp-jira --stdio")
            completed = subprocess.run(
                cmd,  # type: ignore[arg-type]
                input=json.dumps(payload).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                check=False,
            )

            if completed.returncode != 0:
                logger.error(
                    "MCP client returned non-zero exit status: %s, stderr=%s",
                    completed.returncode,
                    completed.stderr.decode("utf-8", errors="ignore"),
                )
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
        """
        Create a Jira issue via MCP.

        Args:
            project_key (str): Jira project key (e.g., "PROJ").
            summary (str): Issue summary/title.
            description (str): Issue description.
            issue_type (str): Jira issue type (default "Task").

        Returns:
            Optional[str]: Issue key (e.g., "PROJ-123") if successful, otherwise None.
        """
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
        """
        Transition a Jira issue to a given workflow status.

        Args:
            issue_key (str): Issue key to transition (e.g., "PROJ-123").
            status_name (str): Target workflow status name (e.g., "In Progress").

        Returns:
            bool: True if transition succeeded, False otherwise.
        """
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
        """
        Add a comment to a Jira issue via MCP.

        Args:
            issue_key (str): Jira issue key (e.g., "PROJ-123").
            comment (str): Comment text.

        Returns:
            bool: True if comment added successfully, False otherwise.
        """
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
    """
    Map an internal TaskStatus string (e.g., 'in_progress') to a Jira workflow status name.

    Args:
        status (str): Internal status string.

    Returns:
        str: Jira status label (e.g., "In Progress"). Defaults to title-cased input if unknown.
    """
    return STATUS_TO_JIRA.get(status, status.title())
