# Generated by Django 4.0.3 on 2022-07-29 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup_sheets', '0010_part_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partrevision',
            name='part',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='setup_sheets.part'),
        ),
    ]
