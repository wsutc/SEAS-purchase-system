# Generated by Django 4.0.3 on 2022-05-25 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0034_purchaserequest_urgency'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaserequestaccounts',
            name='distribution_percent',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='email',
            field=models.EmailField(blank=True, max_length=60, null=True),
        ),
    ]
