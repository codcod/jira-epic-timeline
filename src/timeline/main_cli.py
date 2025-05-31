from timeline import (
    connect_to_jira,
    calculate_epic_timeline,
    display_results,
)
import argparse
import sys
import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables


def main():
    parser = argparse.ArgumentParser(description='Generate a timeline for a JIRA Epic.')
    parser.add_argument('epic_key', help='The JIRA Epic ID (e.g., DIG-123)')
    parser.add_argument('--url', help='JIRA URL', default=os.environ.get('JIRA_URL'))
    parser.add_argument(
        '--username', help='JIRA username', default=os.environ.get('JIRA_USERNAME')
    )
    parser.add_argument(
        '--token', help='JIRA API token', default=os.environ.get('JIRA_API_TOKEN')
    )

    args = parser.parse_args()

    # Check if credentials are provided
    if not all([args.url, args.username, args.token]):
        print(
            'Error: JIRA credentials are required. Provide them as arguments or set environment variables.'
        )
        print('Required: JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN')
        sys.exit(1)

    # Connect to JIRA
    jira = connect_to_jira(args.url, args.username, args.token)

    # Calculate the timeline
    timeline_data = calculate_epic_timeline(jira, args.epic_key)

    # Display the results
    display_results(timeline_data)


if __name__ == '__main__':
    main()
