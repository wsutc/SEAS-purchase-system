# Generated by Django 4.0.3 on 2022-09-26 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('globals', '0005_alter_defaultvalue_date_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='defaultvalue',
            old_name='date_type',
            new_name='data_type',
        ),
    ]
