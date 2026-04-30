import json
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from memory_management.utils.file_utill import FileUtil


@dataclass
class SampleEntity:
    id: str
    value: str


class TestCheckFileExist:
    def test_returns_true_when_file_exists(self, tmp_path):
        file = tmp_path / "data.json"
        file.write_text("{}")
        util = FileUtil(str(tmp_path))
        assert util._FileUtil__check_file_exist("data.json") is True

    def test_returns_false_when_file_does_not_exist(self, tmp_path):
        util = FileUtil(str(tmp_path))
        assert util._FileUtil__check_file_exist("missing.json") is False


class TestCreateFile:
    def test_creates_file_at_path(self, tmp_path):
        util = FileUtil(str(tmp_path))
        util._FileUtil__create_file("data.json")
        assert (tmp_path / "data.json").exists()

    def test_creates_parent_directories(self, tmp_path):
        util = FileUtil(str(tmp_path))
        util._FileUtil__create_file("nested/dir/data.json")
        assert (tmp_path / "nested" / "dir" / "data.json").exists()

    def test_creates_file_with_empty_json_list(self, tmp_path):
        util = FileUtil(str(tmp_path))
        util._FileUtil__create_file("data.json")
        content = (tmp_path / "data.json").read_text()
        assert json.loads(content) == []


class TestWriteJsonToFile:
    def test_writes_data_to_existing_file(self, tmp_path):
        (tmp_path / "data.json").write_text("[]")
        util = FileUtil(str(tmp_path))
        data = [{"id": "1", "value": "hello"}]

        util.write_json_to_file(data, "data.json")

        content = json.loads((tmp_path / "data.json").read_text())
        assert content == data

    def test_creates_file_when_it_does_not_exist(self, tmp_path):
        util = FileUtil(str(tmp_path))
        data = [{"id": "1", "value": "hello"}]

        util.write_json_to_file(data, "new_file.json")

        assert (tmp_path / "new_file.json").exists()
        assert json.loads((tmp_path / "new_file.json").read_text()) == data

    def test_creates_directory_and_file_when_they_do_not_exist(self, tmp_path):
        util = FileUtil(str(tmp_path))
        data = [{"id": "1", "value": "hello"}]

        util.write_json_to_file(data, "subdir/data.json")

        assert (tmp_path / "subdir" / "data.json").exists()
        assert json.loads((tmp_path / "subdir" / "data.json").read_text()) == data

    def test_overwrites_existing_content(self, tmp_path):
        (tmp_path / "data.json").write_text('[{"id": "old"}]')
        util = FileUtil(str(tmp_path))

        util.write_json_to_file([{"id": "new"}], "data.json")

        assert json.loads((tmp_path / "data.json").read_text()) == [{"id": "new"}]


class TestReadJsonFromFile:
    def test_reads_valid_entries_matching_schema(self, tmp_path):
        data = [{"id": "1", "value": "hello"}, {"id": "2", "value": "world"}]
        (tmp_path / "data.json").write_text(json.dumps(data))
        util = FileUtil(str(tmp_path))

        result = util.read_json_from_file("data.json", SampleEntity)

        assert result == [SampleEntity(id="1", value="hello"), SampleEntity(id="2", value="world")]

    def test_creates_file_and_returns_empty_list_when_file_does_not_exist(self, tmp_path):
        util = FileUtil(str(tmp_path))

        result = util.read_json_from_file("missing.json", SampleEntity)

        assert result == []
        assert (tmp_path / "missing.json").exists()

    def test_filters_out_entries_with_missing_required_fields(self, tmp_path, caplog):
        data = [
            {"id": "1", "value": "valid"},
            {"id": "2"},
            {"value": "no_id"},
            {},
        ]
        (tmp_path / "data.json").write_text(json.dumps(data))
        util = FileUtil(str(tmp_path))

        with caplog.at_level(logging.WARNING):
            result = util.read_json_from_file("data.json", SampleEntity)

        assert result == [SampleEntity(id="1", value="valid")]
        assert len(caplog.records) == 3

    def test_filters_out_non_dict_entries(self, tmp_path, caplog):
        data = [{"id": "1", "value": "valid"}, "not_a_dict", 42, None]
        (tmp_path / "data.json").write_text(json.dumps(data))
        util = FileUtil(str(tmp_path))

        with caplog.at_level(logging.WARNING):
            result = util.read_json_from_file("data.json", SampleEntity)

        assert result == [SampleEntity(id="1", value="valid")]
        assert len(caplog.records) == 3
