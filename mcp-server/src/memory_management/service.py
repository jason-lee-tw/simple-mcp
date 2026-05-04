import dataclasses
from typing import List, Tuple
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
        memory_score_list: List[Tuple[MemoryEntry, int]] = []

        for memory in self.__memory_list:            
            memory_content = memory.content.lower()
            score = sum(1 for keyword in query.split() if keyword in memory_content)
            if score > 0:
                memory_score_list.append((memory, score))

        memory_score_list.sort(key=lambda x: x[1], reverse=True)

        print(f'query: {query}\nmemory_score_list: {memory_score_list}')

        return [score_item[0] for score_item in memory_score_list[:limit]]
