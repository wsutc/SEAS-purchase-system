# Generated by Django 4.0.3 on 2022-06-27 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0029_documentnumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrier',
            name='carrier_code',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
