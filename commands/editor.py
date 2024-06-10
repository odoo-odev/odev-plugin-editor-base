from odev.common.commands import LocalDatabaseCommand

from odev.plugins.ps_tech_odev_editor_base.common.editor import Editor


class EditorCommand(LocalDatabaseCommand):
    """Create configuration files to link the database with a project in the current source code editor
    and open the editor with the project loaded.
    """

    _name = "editor"
    _aliases = ["edit"]

    def run(self):
        editor_subclasses = Editor.__subclasses__()

        if not editor_subclasses:
            raise self.error("No editor is supported, please activate an editor plugin and retry")
        elif len(editor_subclasses) > 1:
            raise self.error("Multiple editor plugins are activated, please deactivate all but one and retry")

        editor_class = Editor.__subclasses__()[0]
        editor = editor_class(self._database)
        editor.open()
