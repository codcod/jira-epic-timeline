# JIRA Epic Timeline

A command-line tool that analyzes JIRA epics to determine their actual timeline
based on the transitions of child issues.

## Overview

This tool connects to JIRA and for a given Epic key:
- Identifies all child issues
- Analyzes when each issue transitioned to "In Progress" and to "Done/Closed"
- Calculates the overall timeline for the entire Epic
- Displays a detailed summary with a table of all issues and their individual
timelines

The timeline starts from the earliest date any issue was transitioned to "In
Progress" and ends with the latest date any issue was transitioned to "Done" or
"Closed". If there is no completion date, the Epic is considered to still be "In
Progress".

The tool will display:
- Epic summary and status (In Progress or Done)
- Start and completion dates
- Total duration in days
- A table of all child issues with:
  - Issue key and summary
  - When each issue started and completed
  - Duration for each issue (with * indicating ongoing issues)

![Example output](tl-dark.png)

## Installation and usage

Use Homebrew to install:

```
brew tap codcod/taps
brew install timeline
```

Run the tool:

```
timeline EPIC-123
```

Where `EPIC-123` is the key of the JIRA epic you want to analyze.

See also: [development](docs/development.md).

## Connecting to JIRA

The tool relies on three environment settings that are required to connect to JIRA:
* `JIRA_URL`
* `JIRA_USERNAME`
* `JIRA_API_TOKEN` 

You can export them through the shell, or provide them as arguments to `timeline` command. See `timeline --help` for details.

To obtain a JIRA API token:
1. Log in to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "JIRA Epic Timeline")
4. Copy the token value to your `.env` file, or environment settings.

