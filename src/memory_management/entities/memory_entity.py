from dataclasses import dataclass


@dataclass
class MemoryEntry:
    id: str
    content: str
    timestamp: str
