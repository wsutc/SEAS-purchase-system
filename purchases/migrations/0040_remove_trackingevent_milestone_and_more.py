# Generated by Django 4.0.3 on 2022-08-01 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0039_trackermilestone_trackingevent_milestone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trackingevent',
            name='milestone',
        ),
        migrations.DeleteModel(
            name='TrackerMilestone',
        ),
    ]