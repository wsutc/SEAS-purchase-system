# Generated by Django 4.0.3 on 2022-09-09 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0074_trackerstatussteps_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accounts',
            name='fund',
        ),
        migrations.AlterField(
            model_name='accounts',
            name='account',
            field=models.CharField(help_text='in form XXXX-XXXX.', max_length=10, verbose_name='account'),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='account_title',
            field=models.CharField(help_text='human-readable description of account', max_length=200, verbose_name='account title'),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='budget_code',
            field=models.CharField(help_text='usually first four characters of account', max_length=5, verbose_name='budget code'),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='program_workday',
            field=models.CharField(blank=True, max_length=10, verbose_name='program workday'),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='status',
            field=models.CharField(choices=[('0', 'created'), ('1', 'awaiting approval'), ('2', 'approved'), ('6', 'ordered'), ('7', 'shipped'), ('9', 'partial'), ('8', 'received'), ('3', 'complete'), ('4', 'denied (no resubmission)'), ('5', 'returned (please resubmit')], default='0', max_length=150),
        ),
    ]