from odev.common import args
from odev.common.commands import DatabaseOrRepositoryCommand
from odev.common.version import OdooVersion

from odev.plugins.odev_plugin_editor_base.common.editor import Editor


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
        elif len(editor_subclasses) > 1:
            raise self.error("Multiple editor plugins are activated, please deactivate all but one and retry")

        editor_class = Editor.__subclasses__()[0]

        try:
            editor = editor_class(
                self._database,
                self.args.repository,
                OdooVersion(self.args.version) if self.args.version else None,
            )
        except ValueError as error:
            raise self.error(str(error)) from error

        editor.open()
