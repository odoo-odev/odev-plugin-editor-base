from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, Optional

from odev.common import bash
from odev.common.connectors import GitConnector
from odev.common.databases import Database, DummyDatabase, Repository
from odev.common.logging import logging


logger = logging.getLogger(__name__)


class Editor(ABC):
    """Abstract class meant for interacting with code editors."""

    _name: ClassVar[str]
    """Name of the code editor."""

    _display_name: ClassVar[str]
    """Display name of the code editor."""

    def __init__(self, database: Database, repository: Optional[str] = None):
        """Initialize the editor with a database or repository.
        :param database: The database linked to the project to open in the editor.
        :param repository: The repository to open in the editor.
        """

        if not isinstance(database, DummyDatabase) and repository is not None:
            raise ValueError("Cannot provide both database and repository")

        self.database = database
        """The database linked to the project to open in the editor."""

        self.repository: str
        """The repository to open in the editor."""

        if repository:
            self.repository = repository
        elif database.repository:
            self.repository = (
                database.repository.full_name
                if isinstance(database.repository, Repository)
                else database.repository.name
            )
        else:
            raise ValueError("No database or repository provided, or the database has no repository")

    @property
    def git(self) -> GitConnector:
        """The Git connector for the project."""
        return GitConnector(self.repository)

    @property
    def path(self) -> Path:
        """The path to the project."""
        return self.git.path

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
        logger.info(f"Opening project {self.repository!r} in {self._display_name}")
        return bash.detached(self.command)
