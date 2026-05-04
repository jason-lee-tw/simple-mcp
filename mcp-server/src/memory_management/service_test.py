from unittest.mock import MagicMock, patch

from memory_management.entities.memory_entity import MemoryEntry
from memory_management.service import MemoryManagementService


class TestSaveMemory:
    def test_save_memory_persists_entry(self):
        mock_file_util = MagicMock()
        mock_file_util.read_json_from_file.return_value = []

        with patch('memory_management.service.FileUtil', return_value=mock_file_util):
            service = MemoryManagementService()
            service.save_memory("hello world")

        mock_file_util.write_json_to_file.assert_called_once()
        written_data = mock_file_util.write_json_to_file.call_args[0][0]
        assert len(written_data) == 1
        assert written_data[0]['content'] == "hello world"
        assert 'id' in written_data[0]
        assert 'timestamp' in written_data[0]

    def test_save_memory_appends_to_existing(self):
        existing = MemoryEntry(id="1", content="existing", timestamp="2024-01-01T00:00:00")
        mock_file_util = MagicMock()
        mock_file_util.read_json_from_file.return_value = [existing]

        with patch('memory_management.service.FileUtil', return_value=mock_file_util):
            service = MemoryManagementService()
            service.save_memory("new entry")

        written_data = mock_file_util.write_json_to_file.call_args[0][0]
        assert len(written_data) == 2
        assert written_data[1]['content'] == "new entry"


class TestGetMemory:
    def _make_service(self, entries):
        mock_file_util = MagicMock()
        mock_file_util.read_json_from_file.return_value = entries
        with patch('memory_management.service.FileUtil', return_value=mock_file_util):
            return MemoryManagementService()

    def test_returns_matching_entries(self):
        entries = [
            MemoryEntry(id="1", content="hello world", timestamp="t"),
            MemoryEntry(id="2", content="goodbye world", timestamp="t"),
            MemoryEntry(id="3", content="hello again", timestamp="t"),
            MemoryEntry(id="4", content="The user prefers Python over JavaScript", timestamp="t"),
            MemoryEntry(id="5", content="The user's favourite programming language is Python.", timestamp="t"),
            MemoryEntry(id="6", content="The user love laksa", timestamp="t"),
        ]
        service = self._make_service(entries)

        result = service.get_memory("prefers which programming language")

        assert len(result) == 2
        assert result[0].id == "5"
        assert result[1].id == "4"

    def test_returns_empty_list_on_no_match(self):
        entries = [MemoryEntry(id="1", content="hello world", timestamp="t")]
        service = self._make_service(entries)

        result = service.get_memory("xyz")

        assert result == []

    def test_respects_limit(self):
        entries = [
            MemoryEntry(id=str(i), content=f"hello {i}", timestamp="t")
            for i in range(5)
        ]
        service = self._make_service(entries)

        result = service.get_memory("hello", limit=2)

        assert len(result) == 2

    def test_default_limit_is_3(self):
        entries = [
            MemoryEntry(id=str(i), content=f"hello {i}", timestamp="t")
            for i in range(5)
        ]
        service = self._make_service(entries)

        result = service.get_memory("hello")

        assert len(result) == 3

    def test_case_insensitive_match(self):
        entries = [MemoryEntry(id="1", content="Hello World", timestamp="t")]
        service = self._make_service(entries)

        result = service.get_memory("hello")

        assert len(result) == 1
