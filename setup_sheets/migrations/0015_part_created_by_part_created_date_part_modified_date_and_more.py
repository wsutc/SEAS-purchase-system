# Generated by Django 4.0.3 on 2022-08-25 20:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('setup_sheets', '0014_partrevision_unique_part_revision'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='part',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='part',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='setupsheet',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='tool',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tool',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tool',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='tool',
            name='slug',
            field=models.SlugField(default=django.utils.timezone.now, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='part',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='slug',
            field=models.SlugField(default=django.utils.timezone.now, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='setupsheet',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='setupsheet',
            name='slug',
            field=models.SlugField(editable=False),
        ),
    ]
