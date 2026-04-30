# Memory Service Design

## Goal

Complete the two stub methods in `MemoryManagementService` and fix a bug in `__init__`.

## Changes

### Bug fix: `__init__`

`read_json_from_file` requires a `data_class` argument. Pass `MemoryEntry`:

```python
self.__memory_list = self.__file_util.read_json_from_file('common-memory.json', MemoryEntry)
```

### `save_memory(content: str) -> None`

1. Generate a `uuid4` string as `id`
2. Use `datetime.now().isoformat()` as `timestamp`
3. Construct a `MemoryEntry(id, content, timestamp)`
4. Append to `__memory_list`
5. Serialize full list with `dataclasses.asdict()` per entry
6. Write with `write_json_to_file`

### `get_memory(query: str, limit: int = 3) -> list[MemoryEntry]`

- Case-insensitive substring match: `query.lower() in entry.content.lower()`
- Collect matching entries up to `limit`
- Return type changes from `MemoryEntry | None` to `list[MemoryEntry]`

## Testing

- Test file: `src/memory_management/service_test.py` (follows `*_test.py` naming convention)
- Use `tmp_path` fixture to isolate file I/O
- Cover: save persists entry, get returns matching entries, get respects limit, get returns empty list on no match
