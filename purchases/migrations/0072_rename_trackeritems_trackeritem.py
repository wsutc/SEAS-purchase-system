# Generated by Django 4.0.3 on 2022-09-06 22:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0071_trackeritems_alter_vendororder_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TrackerItems',
            new_name='TrackerItem',
        ),
    ]