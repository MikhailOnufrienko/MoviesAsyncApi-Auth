import abc
import json
from typing import Any


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Получить состояние из хранилища."""
        pass


class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: str | None) -> None:
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в хранилище."""

        with open(self.file_path, 'w+') as file:
            json.dump(state, file)

    def retrieve_state(self):
        """Получить состояние из хранилища."""

        try:
            with open(self.file_path, 'r+') as file:
                data = json.load(file)
        except Exception:
            data = {}

        return data


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""

        state_data = self.storage.retrieve_state()
        state_data[key] = value
        self.storage.save_state(state_data)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""

        state_data = self.storage.retrieve_state()
        state = state_data.get(key)

        return state


json_storate = JsonFileStorage('states.json')
STATE_CLS = State(storage=json_storate)
