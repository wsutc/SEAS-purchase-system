# Generated by Django 4.0.8 on 2023-01-18 23:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0067_vendororder_notes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tracker',
            options={'ordering': ['earliest_event_time']},
        ),
    ]
