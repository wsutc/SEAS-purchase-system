# Generated by Django 4.0.3 on 2022-05-19 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0015_manufacturer_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manufacturer',
            name='slug',
            field=models.SlugField(default='', editable=False, max_length=255, unique=True),
        ),
    ]
