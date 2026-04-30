import dataclasses
import json
import logging
import os

logger = logging.getLogger(__name__)


class FileUtil:
    __dir_path: str

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

    def read_json_from_file[T](self, file_path_in_dir: str, data_class: type[T]) -> list[T]:
        if not self.__check_file_exist(file_path_in_dir):
            self.__create_file(file_path_in_dir)
            return []

        full_path = os.path.join(self.__dir_path, file_path_in_dir)
        with open(full_path, "r") as f:
            raw_list = json.load(f)

        return self.__filter_valid_entries(raw_list, data_class)

    def write_json_to_file[T](self, data: T, file_path_in_dir: str) -> None:
        if not self.__check_file_exist(file_path_in_dir):
            self.__create_file(file_path_in_dir)

        full_path = os.path.join(self.__dir_path, file_path_in_dir)
        with open(full_path, "w") as f:
            json.dump(data, f)

    def __create_file(self, file_path_in_dir: str) -> None:
        full_path = os.path.join(self.__dir_path, file_path_in_dir)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            json.dump([], f)

    def __check_file_exist(self, file_path_in_dir: str) -> bool:
        return os.path.exists(os.path.join(self.__dir_path, file_path_in_dir))

    def __filter_valid_entries[T](self, raw_list: list, data_class: type[T]) -> list[T]:
        if not dataclasses.is_dataclass(data_class):
            return raw_list

        expected_fields = {f.name for f in dataclasses.fields(data_class)}
        valid = []
        for item in raw_list:
            if isinstance(item, dict) and expected_fields.issubset(item.keys()):
                valid.append(data_class(**{k: v for k, v in item.items() if k in expected_fields}))
            else:
                logger.warning("Item does not fit schema %s, skipping: %s", data_class.__name__, item)
        return valid
