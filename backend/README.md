# Backend Linting and Formatting

This backend uses Ruff (linter + formatter) and Black configuration via pyproject.toml.

Common commands:
- make lint        # Run Ruff checks
- make lint-fix    # Run Ruff with autofix
- make format      # Format code with Ruff formatter

You need Python 3.9+ and the following tools installed in your environment:
- ruff
- black (config provided, though formatting is handled by ruff format)

Install Ruff:
  pip install ruff

Optional (Black):
  pip install black
