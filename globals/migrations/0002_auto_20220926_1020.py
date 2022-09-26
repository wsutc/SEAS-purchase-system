# Generated by Django 4.0.3 on 2022-09-26 17:20

from django.db import migrations


def create_new_state_values(apps, schema_editor):
    PurchasesState = apps.get_model("purchases", "state")
    State = apps.get_model("globals", "state")

    all_states = PurchasesState.objects.all()

    for state in all_states:
        new_state, _ = State.objects.get_or_create(
            name = state.name,
            defaults = {
                "abbreviation": state.abbreviation
            }
        )
        print(f"{new_state.name}|{new_state.abbreviation}")


class Migration(migrations.Migration):

    dependencies = [
        ('globals', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_new_state_values),
    ]
