# Generated by Django 4.0.3 on 2022-07-29 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('setup_sheets', '0006_remove_setupsheet_part_number_and_more'),
    ]

    operations = [
        migrations.RunSQL("ALTER TABLE `seas_purchasing`.`setup_sheets_setupsheet` ADD part_number CHAR;"),
        migrations.RemoveField(
            model_name='setupsheet',
            name='part_number',
        ),
    ]