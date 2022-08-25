# Generated by Django 4.0.3 on 2022-08-24 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0047_alter_trackingevent_stage'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='tracker',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='carrier',
            name='slug',
            field=models.SlugField(blank=True, null=True, verbose_name='Carrier Slug'),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='sales_tax_rate',
            field=models.DecimalField(decimal_places=3, default='.087', max_digits=5),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='status',
            field=models.CharField(choices=[('0', 'Wish List/Created'), ('1', 'Awaiting Approval'), ('2', 'Approved'), ('6', 'Ordered'), ('7', 'Shipped'), ('8', 'Received'), ('9', 'Partial'), ('3', 'Complete'), ('4', 'Denied (no resubmission)'), ('5', 'Returned (please resubmit)')], default='0', max_length=150),
        ),
    ]
