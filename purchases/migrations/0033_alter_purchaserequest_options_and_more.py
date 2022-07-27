# Generated by Django 4.0.3 on 2022-07-22 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0032_alter_accounts_options_alter_spendcategory_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchaserequest',
            options={'ordering': ['-created_date']},
        ),
        migrations.AlterModelOptions(
            name='requisitioner',
            options={'ordering': ['user']},
        ),
        migrations.AlterModelOptions(
            name='state',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='requisitioner',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]
