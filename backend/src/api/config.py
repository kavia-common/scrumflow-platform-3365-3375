from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load env vars from backend/.env if present
load_dotenv()


@dataclass
class JiraConfig:
    """Configuration for Jira MCP integration pulled from environment variables."""
    base_url: str | None
    email: str | None
    api_token: str | None
    project_key: str | None
    mcp_client_cmd: str | None

    @property
    def enabled(self) -> bool:
        """True if all required pieces for Jira MCP are present."""
        return all([
            bool(self.base_url),
            bool(self.email),
            bool(self.api_token),
            bool(self.project_key),
            bool(self.mcp_client_cmd),
        ])


# PUBLIC_INTERFACE
def get_jira_config() -> JiraConfig:
    """Return JiraConfig loaded from environment variables."""
    return JiraConfig(
        base_url=os.getenv("JIRA_BASE_URL"),
        email=os.getenv("JIRA_EMAIL"),
        api_token=os.getenv("JIRA_API_TOKEN"),
        project_key=os.getenv("JIRA_PROJECT_KEY"),
        mcp_client_cmd=os.getenv("MCP_CLIENT_CMD"),
    )
