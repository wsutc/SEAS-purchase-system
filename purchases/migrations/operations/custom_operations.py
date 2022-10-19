from django.db.migrations.operations.base import Operation
from django.db.migrations.operations import AddField


class AddFieldResilient(AddField):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass


class RemoveColumn(Operation):
    def __init__(self, model_name: str, name: str) -> None:
        self.model_name = model_name
        super().__init__(name)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.remove_field(model)

    def describe(self):
        return "Remove database column '{}' from '{}' table.".format(
            self.name,
            self.model_name,
        )

    @property
    def migration_name_fragment(self):
        model_name = self.model_name
        name = self.model_name
        return f"remove_column_{model_name}_{name}"
