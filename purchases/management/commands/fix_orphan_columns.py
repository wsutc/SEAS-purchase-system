from typing import Any  # , Optional

from django.apps import apps

# from django.db.backends
# from django.conf import settings
from django.core.management.base import LabelCommand

from web_project.helpers import print_attributes


class Command(LabelCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument("table", nargs="+", type=str)
    #     parser.add_argument("column_name", nargs="+", type=str)

    # def handle(self, *args: Any, **options: Any) -> Optional[str]:

    #     return super().handle(*args, **options)

    # def database_forwards(self, schema_editor):
    #     from_model = from_state.apps.get_model(app_label, self.model_name)
    #     if self.allow_migrate_model(schema_editor.connection.alias, from_model):
    #         schema_editor.remove_field(
    #             from_model, from_model._meta.get_field(self.name)
    #         )

    def handle_label(self, label: str, **options: Any) -> None:
        purchases_app = apps.get_app_config("purchases")
        model_name, name = label.split(".")
        model_obj = purchases_app.get_model(model_name)

        print_attributes(model_obj)

        # with connection.schema_editor() as schema_editor:
        #     schema_editor.remove_field(

        #     )
