import abc
import json
import os
from pathlib import Path
from typing import Any

from .settings import etl_settings

state_file_name: str = etl_settings.STATE_FILE_NAME
default_file_path: str = f'{Path(__file__).resolve().parent.parent}'


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state to a permanent storage."""

        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Load state locally from the permanent storage."""

        pass


class JsonFileStorage(BaseStorage):
    """A class to save and retrieve states from storage"""

    def __init__(
        self, file_path: str | None,
        file_name: str | None = state_file_name
    ) -> None:
        """Json File Storage Initialization."""

        self.file_path = file_path
        self.file_name = file_name
        self.state_file = f'{self.file_path}{self.file_name}'

    def save_state(self, state: dict) -> None:
        """Save state to the permanent storage."""

        saved_state = self.retrieve_state() or {}

        with open(self.state_file, 'w') as storage:
            state_to_save: dict = {**saved_state, **state}
            json.dump(state_to_save, storage, ensure_ascii=False, indent=4)

    def retrieve_state(self) -> dict | None:
        """Load state locally from the permanent storage."""

        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as storage:
                return json.load(storage)
        else:
            return None


class State:
    """
    A class to store state when working with data,
    so that not to constantly re-read the data.
    """

    def __init__(self, storage: BaseStorage) -> None:
        """State class Initialization."""

        self.storage = storage
        self.state = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Set state for a specific key."""

        self.storage.save_state(state={key: value})

    def get_state(self, key: str) -> Any:
        """Get state on a certain key."""

        if self.state is not None:
            return self.state.get(key)

        return None
