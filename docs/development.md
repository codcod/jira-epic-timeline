## Jira Epic Timeline: Development

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/jira-epic-timeline.git
   cd jira-epic-timeline
   ```

2. Set up a Python environment (requires Python 3.13+):
   ```
   uv venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

### Configuration

Create a `.env` file in the project root with your JIRA credentials:

```
JIRA_URL = "https://your-instance.atlassian.net"
JIRA_USERNAME = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token"
```

You can copy the `.env.sample` file as a template:
```
cp .env.sample .env
```

### Requirements
- Python 3.13+
- Dependencies as listed in `pyproject.toml`

### Linting

Run linting checks with:
```
make lint
```

This will run Ruff to check and format your code.

### Project Structure

- `src/timeline/`: Main package with all the functionality
  - `timeline.py`: Core functions for JIRA interactions and timeline calculations
- `bin/`: Command-line scripts
  - `tl`: Bash script wrapper for the Python tool
  - `tl.py`: Python entry point
