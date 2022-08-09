# Generated by Django 4.0.3 on 2022-06-17 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0013_requisitioner_wsu_id_alter_tracker_events_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracker',
            name='delivery_estimate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=40, verbose_name='Name of Product'),
        ),
        migrations.AlterField(
            model_name='requisitioner',
            name='wsu_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='WSU ID'),
        ),
        migrations.AlterField(
            model_name='tracker',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
