"""Tests for mock discovery via comments."""

import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from linter.state.file_state import FileLinterState
from linter.state.global_state import GlobalLinterState
from linter.pipelines.discovery_pipeline import DiscoveryPipeline
from tests.assets.linter.mock.metadata import METADATA


class TestMockCommentDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA
        self.linter = Linter(self.metadata)

    def test_discovery__create_comment__adds_mock(self) -> None:
        content = "# stdlib _mock.create: mymock\n"
        file_state = FileLinterState()
        global_state = GlobalLinterState(self.metadata)
        discovery = DiscoveryPipeline(global_state, file_state)

        discovery.process(content)

        self.assertEqual(len(file_state.mock_scopes), 1)
        self.assertEqual(file_state.mock_scopes[0].name, "mymock")
        self.assertEqual(file_state.mock_scopes[0].end_offset, -1)

    def test_discovery__create_multiple_comment__adds_mocks(self) -> None:
        content = "# stdlib _mock.create: mock1, mock2, mock3\n"
        file_state = FileLinterState()
        global_state = GlobalLinterState(self.metadata)
        discovery = DiscoveryPipeline(global_state, file_state)

        discovery.process(content)

        self.assertEqual(len(file_state.mock_scopes), 3)
        self.assertEqual(file_state.mock_scopes[0].name, "mock1")
        self.assertEqual(file_state.mock_scopes[1].name, "mock2")
        self.assertEqual(file_state.mock_scopes[2].name, "mock3")

    def test_discovery__delete_comment__ends_mock(self) -> None:
        content = "# stdlib _mock.create: mymock\n# stdlib _mock.delete: mymock\n"
        file_state = FileLinterState()
        global_state = GlobalLinterState(self.metadata)
        discovery = DiscoveryPipeline(global_state, file_state)

        discovery.process(content)

        self.assertEqual(len(file_state.mock_scopes), 1)
        self.assertEqual(file_state.mock_scopes[0].name, "mymock")
        self.assertNotEqual(file_state.mock_scopes[0].end_offset, -1)

    def test_discovery__delete_multiple_comment__ends_mocks(self) -> None:
        content = "# stdlib _mock.create: m1, m2\n# stdlib _mock.delete: m1, m2\n"
        file_state = FileLinterState()
        global_state = GlobalLinterState(self.metadata)
        discovery = DiscoveryPipeline(global_state, file_state)

        discovery.process(content)

        self.assertEqual(len(file_state.mock_scopes), 2)
        self.assertNotEqual(file_state.mock_scopes[0].end_offset, -1)
        self.assertNotEqual(file_state.mock_scopes[1].end_offset, -1)

    def test_discovery__create_comment_with_trailing__adds_mock(self) -> None:
        content = "# stdlib _mock.create: mymock # some note\n"
        file_state = FileLinterState()
        global_state = GlobalLinterState(self.metadata)
        discovery = DiscoveryPipeline(global_state, file_state)

        discovery.process(content)

        self.assertEqual(len(file_state.mock_scopes), 1)
        self.assertEqual(file_state.mock_scopes[0].name, "mymock")

    def test_discovery__inline_create_comment__adds_mock(self) -> None:
        content = "ls # stdlib _mock.create: mymock\n"
        file_state = FileLinterState()
        global_state = GlobalLinterState(self.metadata)
        discovery = DiscoveryPipeline(global_state, file_state)

        discovery.process(content)

        self.assertEqual(len(file_state.mock_scopes), 1)
        self.assertEqual(file_state.mock_scopes[0].name, "mymock")

    def test_discovery__inline_create_multiple_comment__adds_mocks(self) -> None:
        content = "ls # stdlib _mock.create: m1, m2\n"
        file_state = FileLinterState()
        global_state = GlobalLinterState(self.metadata)
        discovery = DiscoveryPipeline(global_state, file_state)

        discovery.process(content)

        self.assertEqual(len(file_state.mock_scopes), 2)
        self.assertEqual(file_state.mock_scopes[0].name, "m1")
        self.assertEqual(file_state.mock_scopes[1].name, "m2")

    def test_lint__mock_via_comment__no_issues(self) -> None:
        content = """
# stdlib _mock.create: mymock
mymock.mock.assert_not_called
"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__mock_used_before_comment__reports_std010(self) -> None:
        content = """
mymock.mock.assert_not_called
# stdlib _mock.create: mymock
"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        codes = [i.CODE for i in issues]
        self.assertIn("STD010", codes)

    def test_lint__mock_used_after_delete_comment__reports_std010(self) -> None:
        content = """
# stdlib _mock.create: mymock
# stdlib _mock.delete: mymock
mymock.mock.assert_not_called
"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        codes = [i.CODE for i in issues]
        self.assertIn("STD010", codes)

if __name__ == "__main__":
    unittest.main()
