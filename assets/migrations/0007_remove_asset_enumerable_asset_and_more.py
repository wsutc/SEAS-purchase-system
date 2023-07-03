# Generated by Django 4.2.2 on 2023-07-03 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0006_asset_enumerable_enumerableassetgroup_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="asset",
            name="enumerable_asset",
        ),
        migrations.AddField(
            model_name="asset",
            name="enumerable_counter",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="enumerable counter"
            ),
        ),
        migrations.AddField(
            model_name="asset",
            name="enumerable_group",
            field=models.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="assets.enumerableassetgroup",
                verbose_name="enumerable group",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="asset",
            name="enumerable_tag",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="enumerable tag"
            ),
        ),
        migrations.DeleteModel(
            name="EnumerableAsset",
        ),
    ]
