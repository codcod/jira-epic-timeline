import unittest
from unittest.mock import MagicMock, patch

from dateutil import parser

from timeline import (
    get_epic_issues,
    extract_transition_dates,
    calculate_epic_timeline,
)


# class TestEpicIssues(unittest.TestCase):
#     def setUp(self):
#         self.mock_jira = MagicMock()
#         self.mock_epic = MagicMock()
#         self.mock_epic.key = 'EPIC-123'
#         self.mock_jira.issue.return_value = self.mock_epic

#     def test_get_epic_issues_success(self):
#         # Arrange
#         mock_issues = [MagicMock(), MagicMock()]
#         self.mock_jira.search_issues.return_value = mock_issues

#         # Act
#         result = get_epic_issues(self.mock_jira, 'EPIC-123')

#         # Assert
#         self.mock_jira.issue.assert_called_once_with('EPIC-123')
#         self.mock_jira.search_issues.assert_called_once_with(
#             '"Epic Link" = EPIC-123 and status not in (Closed) ORDER BY created ASC',
#             maxResults=0,
#         )
#         self.assertEqual(result, mock_issues)

#     @patch('timeline.sys.exit')
#     def test_get_epic_issues_failure(self, mock_exit):
#         # Arrange
#         self.mock_jira.search_issues.side_effect = Exception('Search error')

#         # Act
#         get_epic_issues(self.mock_jira, 'EPIC-123')

#         # Assert
#         mock_exit.assert_called_once_with(1)


class TestTransitionDates(unittest.TestCase):
    def setUp(self):
        self.mock_jira = MagicMock()
        self.mock_issue = MagicMock()
        self.mock_issue.key = 'ISSUE-456'

        # Create mock changelog
        self.mock_changelog = MagicMock()
        self.mock_changelog.histories = []

        mock_issue_with_changelog = MagicMock()
        mock_issue_with_changelog.changelog = self.mock_changelog
        self.mock_jira.issue.return_value = mock_issue_with_changelog

    def test_extract_transition_dates_with_transitions(self):
        # Arrange
        # Create history items for transitions
        history1 = MagicMock()
        history1.created = '2023-01-15T10:00:00.000+0000'
        item1 = MagicMock()
        item1.field = 'status'
        item1.toString = 'In Progress'
        item1.fromString = 'To Do'
        history1.items = [item1]

        history2 = MagicMock()
        history2.created = '2023-02-20T14:00:00.000+0000'
        item2 = MagicMock()
        item2.field = 'status'
        item2.toString = 'Done'
        item2.fromString = 'In Progress'
        history2.items = [item2]

        self.mock_changelog.histories = [history1, history2]

        # Act
        in_progress_date, done_date = extract_transition_dates(
            self.mock_jira, self.mock_issue
        )

        # Assert
        self.assertEqual(in_progress_date, parser.parse('2023-01-15T10:00:00.000+0000'))
        self.assertEqual(done_date, parser.parse('2023-02-20T14:00:00.000+0000'))

    def test_extract_transition_dates_without_transitions(self):
        # Arrange - empty changelog
        self.mock_changelog.histories = []

        # Act
        in_progress_date, done_date = extract_transition_dates(
            self.mock_jira, self.mock_issue
        )

        # Assert
        self.assertIsNone(in_progress_date)
        self.assertIsNone(done_date)


# class TestEpicTimeline(unittest.TestCase):
#     @patch('timeline.get_epic_issues')
#     @patch('timeline.extract_transition_dates')
#     def test_calculate_epic_timeline_active_epic(
#         self, mock_extract_dates, mock_get_issues
#     ):
#         # Arrange
#         mock_jira = MagicMock()

#         # Mock epic
#         mock_epic = MagicMock()
#         mock_epic.fields.summary = 'Test Epic'
#         mock_jira.issue.return_value = mock_epic

#         # Mock issues
#         mock_issue1 = MagicMock()
#         mock_issue1.key = 'ISSUE-1'
#         mock_issue1.fields.summary = 'Issue 1'
#         mock_issue1.fields.issuetype.name = 'Task'
#         mock_issue1.fields.status.name = 'In Progress'

#         mock_issue2 = MagicMock()
#         mock_issue2.key = 'ISSUE-2'
#         mock_issue2.fields.summary = 'Issue 2'
#         mock_issue2.fields.issuetype.name = 'Bug'
#         mock_issue2.fields.status.name = 'Done'

#         mock_get_issues.return_value = [mock_issue1, mock_issue2]

#         # Mock transition dates
#         in_progress_date1 = parser.parse('2023-01-10T10:00:00.000+0000')
#         in_progress_date2 = parser.parse('2023-01-15T10:00:00.000+0000')
#         done_date2 = parser.parse('2023-02-20T14:00:00.000+0000')

#         mock_extract_dates.side_effect = [
#             (in_progress_date1, None),  # Issue 1 is in progress
#             (in_progress_date2, done_date2),  # Issue 2 is done
#         ]

#         # Act
#         result = calculate_epic_timeline(mock_jira, 'EPIC-123')

#         # Assert
#         self.assertEqual(result['epic_key'], 'EPIC-123')
#         self.assertEqual(result['epic_summary'], 'Test Epic')
#         self.assertEqual(result['earliest_in_progress'], in_progress_date1)
#         self.assertEqual(result['latest_done'], done_date2)
#         self.assertEqual(
#             result['status'], 'In Progress'
#         )  # Epic is in progress because issue 1 is not done
#         self.assertEqual(len(result['issue_timelines']), 2)

#     @patch('timeline.get_epic_issues')
#     @patch('timeline.extract_transition_dates')
#     def test_calculate_epic_timeline_completed_epic(
#         self, mock_extract_dates, mock_get_issues
#     ):
#         # Arrange
#         mock_jira = MagicMock()

#         # Mock epic
#         mock_epic = MagicMock()
#         mock_epic.fields.summary = 'Test Epic'
#         mock_jira.issue.return_value = mock_epic

#         # Mock issues
#         mock_issue1 = MagicMock()
#         mock_issue1.key = 'ISSUE-1'
#         mock_issue1.fields.summary = 'Issue 1'
#         mock_issue1.fields.issuetype.name = 'Task'
#         mock_issue1.fields.status.name = 'Done'

#         mock_issue2 = MagicMock()
#         mock_issue2.key = 'ISSUE-2'
#         mock_issue2.fields.summary = 'Issue 2'
#         mock_issue2.fields.issuetype.name = 'Bug'
#         mock_issue2.fields.status.name = 'Done'

#         mock_get_issues.return_value = [mock_issue1, mock_issue2]

#         # Mock transition dates - all issues are done
#         in_progress_date1 = parser.parse('2023-01-10T10:00:00.000+0000')
#         in_progress_date2 = parser.parse('2023-01-15T10:00:00.000+0000')
#         done_date1 = parser.parse('2023-02-15T14:00:00.000+0000')
#         done_date2 = parser.parse('2023-02-20T14:00:00.000+0000')

#         mock_extract_dates.side_effect = [
#             (in_progress_date1, done_date1),
#             (in_progress_date2, done_date2),
#         ]

#         # Act
#         result = calculate_epic_timeline(mock_jira, 'EPIC-123')

#         # Assert
#         self.assertEqual(result['epic_key'], 'EPIC-123')
#         self.assertEqual(result['earliest_in_progress'], in_progress_date1)
#         self.assertEqual(result['latest_done'], done_date2)
#         self.assertEqual(
#             result['status'], 'Done'
#         )  # Epic is done because all issues are done
#         self.assertEqual(result['duration_days'], 41)  # Days between Jan 10 and Feb 20


if __name__ == '__main__':
    unittest.main()
