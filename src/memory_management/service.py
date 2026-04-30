import dataclasses
import uuid
from datetime import datetime
from os import path
from pathlib import Path

from memory_management.entities.memory_entity import MemoryEntry
from memory_management.utils.file_utill import FileUtil


class MemoryManagementService:
    __file_util: FileUtil
    __memory_list: list[MemoryEntry]

    def __init__(self):
        self.__file_util = FileUtil(path.join(Path(__file__).parent, '../../temp/memory'))
        self.__memory_list = self.__file_util.read_json_from_file('common-memory.json', MemoryEntry)

    def save_memory(self, content: str) -> None:
        entry = MemoryEntry(
            id=str(uuid.uuid7()),
            content=content,
            timestamp=datetime.now().isoformat(),
        )
        self.__memory_list.append(entry)
        self.__file_util.write_json_to_file(
            [dataclasses.asdict(e) for e in self.__memory_list],
            'common-memory.json',
        )

    def get_memory(self, query: str, limit: int = 3) -> list[MemoryEntry]:
        results = []
        for entry in self.__memory_list:
            if query.lower() in entry.content.lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
