from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from odev.common import bash
from odev.common.connectors import GitConnector
from odev.common.databases import LocalDatabase
from odev.common.logging import logging


logger = logging.getLogger(__name__)


class Editor(ABC):
    """Abstract class meant for interacting with code editors."""

    _name: ClassVar[str]
    """Name of the code editor."""

    _display_name: ClassVar[str]
    """Display name of the code editor."""

    def __init__(self, database: LocalDatabase):
        self.database = database
        """The database linked to the project to open in the editor."""

    @property
    def path(self) -> Path:
        """The path to the project."""
        assert self.database.repository is not None
        return GitConnector(self.database.repository.full_name).path

    @property
    def command(self) -> str:
        """The command to open the editor with the project loaded."""
        return f"{self._name} {self.path}"

    @property
    def exists(self) -> bool:
        """Check if the project exists."""
        return self.path.exists()

    @property
    def installed(self) -> bool:
        """Check if the editor is installed."""
        process = bash.execute(f"{self._name} -v")
        return process is not None and process.returncode == 0

    @abstractmethod
    def configure(self):
        """Configure the editor to work with the database."""
        raise NotImplementedError

    def open(self):
        """Open the editor with the project loaded."""
        self.configure()
        assert self.database.repository is not None
        logger.info(f"Opening project {self.database.repository.full_name!r} in {self._display_name}")
        return bash.detached(self.command)
