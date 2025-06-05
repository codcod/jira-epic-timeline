import datetime
import sys
from typing import Dict, List, Optional, Tuple

from dateutil import parser
from jira import JIRA
from rich.console import Console
from rich.table import Table


def connect_to_jira(jira_url: str, username: str, api_token: str) -> JIRA:
    """Connect to JIRA using the provided credentials."""
    try:
        return JIRA(server=jira_url, basic_auth=(username, api_token))
    except Exception as e:
        print(f'Error connecting to JIRA: {e}')
        sys.exit(1)


def get_epic_issues(jira: JIRA, epic_id: str) -> List:
    """Get all issues that belong to the given epic."""
    try:
        epic = jira.issue(epic_id)
        epic_key = epic.key

        # JQL query to find all issues linked to this epic
        jql_query = (
            f'"Epic Link" = {epic_key} and status not in (Closed) ORDER BY created ASC'
        )
        return list(jira.search_issues(jql_query, maxResults=0))
    except Exception as e:
        print(f'Error retrieving epic issues: {e}')
        sys.exit(1)


def extract_transition_dates(
    jira: JIRA, issue
) -> Tuple[Optional[datetime.datetime], Optional[datetime.datetime]]:
    """Extract the dates when the issue was set to 'In Progress' and 'Done/Closed'."""
    try:
        # Get the changelog of the issue
        changelog = jira.issue(issue.key, expand='changelog').changelog

        # Initialize dates
        in_progress_date = None
        done_date = None

        # Loop through all history entries
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    # Check transition to 'In Progress'
                    if item.toString == 'In Progress' and item.fromString in [
                        'Open',
                        'To Do',
                        'Backlog',
                        'In Discovery',
                    ]:
                        # Use the latest transition to In Progress
                        current_date = parser.parse(history.created)
                        if in_progress_date is None or current_date > in_progress_date:
                            in_progress_date = current_date

                    # Check transition to 'Done' or 'Closed'
                    if item.toString in ['Done', 'Closed']:
                        # Use the latest transition to Done or Closed
                        current_date = parser.parse(history.created)
                        if done_date is None or current_date > done_date:
                            done_date = current_date

        return in_progress_date, done_date
    except Exception as e:
        print(f'Error extracting transition dates for {issue.key}: {e}')
        return None, None


def calculate_epic_timeline(jira: JIRA, epic_id: str) -> Dict:
    """Calculate the timeline for the entire epic."""
    issues = get_epic_issues(jira, epic_id)

    if not issues:
        print(f'No issues found for epic {epic_id}')
        sys.exit(0)

    # Get epic details
    epic = jira.issue(epic_id)
    epic_summary = epic.fields.summary

    earliest_in_progress = None
    latest_done = None
    issue_timelines = []

    for issue in issues:
        in_progress_date, done_date = extract_transition_dates(jira, issue)

        # Add to issue timelines
        issue_timelines.append(
            {
                'key': issue.key,
                'summary': issue.fields.summary,
                'in_progress': in_progress_date,
                'done': done_date,
                'type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
            }
        )

        # Update earliest in progress date
        if in_progress_date:
            if not earliest_in_progress or in_progress_date < earliest_in_progress:
                earliest_in_progress = in_progress_date

        # Update latest done date
        if done_date:
            if not latest_done or done_date > latest_done:
                latest_done = done_date

    # Calculate duration in days
    duration = None
    status = 'In Progress'

    if earliest_in_progress:
        if latest_done:
            duration = (latest_done - earliest_in_progress).days
            status = 'Done'
        else:
            # Calculate duration until today
            duration = (
                datetime.datetime.now(earliest_in_progress.tzinfo)
                - earliest_in_progress
            ).days

    return {
        'epic_key': epic_id,
        'epic_summary': epic_summary,
        'earliest_in_progress': earliest_in_progress,
        'latest_done': latest_done,
        'duration_days': duration,
        'status': status,
        'issue_timelines': issue_timelines,
    }


def display_results(timeline_data: Dict) -> None:
    """Display the epic timeline results."""
    console = Console()

    console.print(
        f'\n[bold blue]Epic Timeline: {timeline_data["epic_key"]} - {timeline_data["epic_summary"]}[/bold blue]'
    )
    console.print(
        f'Status: [bold {"green" if timeline_data["status"] == "Done" else "yellow"}]{timeline_data["status"]}[/bold {"green" if timeline_data["status"] == "Done" else "yellow"}]'
    )

    if timeline_data['earliest_in_progress']:
        console.print(
            f'Started: [bold]{timeline_data["earliest_in_progress"].strftime("%Y-%m-%d")}[/bold]'
        )
    else:
        console.print('Started: [italic]Not started yet[/italic]')

    if timeline_data['latest_done']:
        console.print(
            f'Completed: [bold]{timeline_data["latest_done"].strftime("%Y-%m-%d")}[/bold]'
        )
    else:
        console.print('Completed: [italic]Not completed yet[/italic]')

    if timeline_data['duration_days'] is not None:
        console.print(f'Duration: [bold]{timeline_data["duration_days"]}[/bold] days')

    # Create table for issues
    table = Table(title='Issues Timeline')
    table.add_column('Issue Key', style='cyan')
    table.add_column('Type', style='white')
    table.add_column('Summary', style='white')
    table.add_column('Started', style='green')
    table.add_column('Completed', style='blue')
    table.add_column('Status', style='white')
    table.add_column('Duration (days)', style='yellow')

    issue_timelines = timeline_data['issue_timelines']
    sorted_data = sorted(
        issue_timelines, key=lambda x: (x['in_progress'] is None, x['in_progress'])
    )

    for issue in sorted_data:
        in_progress_str = (
            issue['in_progress'].strftime('%Y-%m-%d')
            if issue['in_progress']
            else 'Not started'
        )
        done_str = (
            issue['done'].strftime('%Y-%m-%d') if issue['done'] else 'Not completed'
        )

        duration = ''
        if issue['in_progress']:
            if issue['done']:
                duration = str((issue['done'] - issue['in_progress']).days)
            else:
                duration = (
                    str(
                        (
                            datetime.datetime.now(issue['in_progress'].tzinfo)
                            - issue['in_progress']
                        ).days
                    )
                    + '*'
                )

        table.add_row(
            issue['key'],
            issue['type'],
            issue['summary'],
            in_progress_str,
            done_str,
            issue['status'],
            duration,
        )

    console.print(table)
