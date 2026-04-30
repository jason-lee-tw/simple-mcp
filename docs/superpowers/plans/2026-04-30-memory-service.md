# Memory Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the two stub methods in `MemoryManagementService` and fix a bug in `__init__`.

**Architecture:** Use TDD — write failing tests first, then implement. Tests use `unittest.mock.patch` (stdlib, no extra deps) to replace `FileUtil` with a `MagicMock`, avoiding any real file I/O. The service appends to its in-memory list on save and serialises via `dataclasses.asdict()` before writing.

**Tech Stack:** Python 3.14, `uuid` (stdlib), `datetime` (stdlib), `dataclasses` (stdlib), `unittest.mock` (stdlib), `pytest`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `src/memory_management/service.py` | Fix `__init__` bug; implement `save_memory` and `get_memory` |
| Create | `src/memory_management/service_test.py` | Unit tests for the service |

---

### Task 1: Fix `__init__` bug and implement `save_memory`

**Files:**
- Modify: `src/memory_management/service.py`
- Create: `src/memory_management/service_test.py`

- [ ] **Step 1: Create the test file with failing tests for `save_memory`**

Create `src/memory_management/service_test.py`:

```python
import dataclasses
from unittest.mock import MagicMock, patch

import pytest

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
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd /Users/jason/projects/thoughtworks/ai-angineering-upskill-program/simple-mcp
uv run pytest src/memory_management/service_test.py -v
```

Expected: FAIL — `save_memory` returns `None` / makes no calls.

- [ ] **Step 3: Implement the fix and `save_memory`**

Replace the full content of `src/memory_management/service.py`:

```python
import dataclasses
import uuid
from datetime import datetime
from os import path
from pathlib import Path
from typing import List

from memory_management.entities.memory_entity import MemoryEntry
from memory_management.utils.file_utill import FileUtil


class MemoryManagementService:
    __file_util: FileUtil
    __memory_list: List[MemoryEntry]

    def __init__(self):
        self.__file_util = FileUtil(path.join(Path(__file__).parent, '../../temp/memory'))
        self.__memory_list = self.__file_util.read_json_from_file('common-memory.json', MemoryEntry)

    def save_memory(self, content: str) -> None:
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.now().isoformat(),
        )
        self.__memory_list.append(entry)
        self.__file_util.write_json_to_file(
            [dataclasses.asdict(e) for e in self.__memory_list],
            'common-memory.json',
        )

    def get_memory(self, query: str, limit: int = 3) -> list[MemoryEntry]:
        pass
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
uv run pytest src/memory_management/service_test.py::TestSaveMemory -v
```

Expected: PASS (2 tests).

---

### Task 2: Implement `get_memory`

**Files:**
- Modify: `src/memory_management/service.py`
- Modify: `src/memory_management/service_test.py`

- [ ] **Step 1: Add failing tests for `get_memory`**

Append to `src/memory_management/service_test.py`:

```python
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
        ]
        service = self._make_service(entries)

        result = service.get_memory("hello")

        assert len(result) == 2
        assert result[0].id == "1"
        assert result[1].id == "3"

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
```

- [ ] **Step 2: Run to confirm they fail**

```bash
uv run pytest src/memory_management/service_test.py::TestGetMemory -v
```

Expected: FAIL — `get_memory` returns `None`.

- [ ] **Step 3: Implement `get_memory`**

Replace the `get_memory` stub in `src/memory_management/service.py`:

```python
    def get_memory(self, query: str, limit: int = 3) -> list[MemoryEntry]:
        results = []
        for entry in self.__memory_list:
            if query.lower() in entry.content.lower():
                results.append(entry)
            if len(results) >= limit:
                break
        return results
```

- [ ] **Step 4: Run the full test suite**

```bash
uv run pytest src/memory_management/service_test.py -v
```

Expected: PASS (7 tests).

- [ ] **Step 5: Run all project tests to check for regressions**

```bash
uv run pytest src/ -v
```

Expected: all tests pass.
