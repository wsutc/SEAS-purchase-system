# Generated by Django 4.0.3 on 2022-07-29 16:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setup_sheets", "0003_part_remove_setupsheet_material_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="setupsheet",
            options={"ordering": ["operation"]},
        ),
        # migrations.AlterField(
        #     model_name='setupsheet',
        #     name=''
        # ),
        # migrations.RunSQL("DROP TABLE `seas_purchasing`.`setup_sheets_part`;"),
        # migrations.CreateModel(
        #     name='Part',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=150)),
        #         ('number', models.CharField(max_length=50, unique=True)),
        #         ('material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='setup_sheets.material')),
        #     ],
        # ),
        # migrations.AddField(
        #     model_name='partrevision',
        #     name='part',
        #     field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='setup_sheets.part'),
        # ),
    ]
