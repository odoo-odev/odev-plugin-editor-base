from odev.common import args
from odev.common.commands import DatabaseOrRepositoryCommand
from odev.common.databases import LocalDatabase
from odev.common.logging import logging
from odev.common.version import OdooVersion

from odev.plugins.odev_plugin_editor_base.common.editor import Editor


logger = logging.getLogger(__name__)


class EditorCommand(DatabaseOrRepositoryCommand):
    """Create configuration files to link the database with a project in the current source code editor
    and open the editor with the project loaded.
    """

    _name = "code"

    _database_allowed_platforms = ["local"]

    _exclusive_arguments = [("database", "version")]

    version = args.String(
        aliases=["-V", "--version"],
        description="Odoo version to open a workspace for.",
    )

    @classmethod
    def prepare_command(cls, *args, **kwargs) -> None:
        super().prepare_command(*args, **kwargs)
        cls.remove_argument("platform")
        cls.remove_argument("branch")

    def run(self):
        editor_subclasses = Editor.__subclasses__()

        if not editor_subclasses:
            raise self.error("No editor is supported, please activate an editor plugin and retry")
        if len(editor_subclasses) > 1:
            raise self.error("Multiple editor plugins are activated, please deactivate all but one and retry")

        editor_class = Editor.__subclasses__()[0]
        self.link_repository()

        try:
            editor = editor_class(
                self._database,
                self.args.repository,
                OdooVersion(self.args.version) if self.args.version else None,
            )
        except ValueError as error:
            raise self.error(str(error)) from error

        editor.open()

    def link_repository(self) -> None:
        """Save the repository given on the command line as the one linked to the database.

        Passing a repository used to apply to that single invocation only, so the next `odev code`
        on the same database had to be given the repository again. The link is now persisted, which
        is also what makes the database usable with the other commands relying on it.
        """
        if not isinstance(self._database, LocalDatabase) or not self.args.repository:
            return

        previous = self._database.repository
        repository = self._database.link_repository(self.args.repository)

        if repository is not None and repository != previous:
            logger.info(f"Linked database {self._database.name!r} to repository {repository.full_name!r}")
