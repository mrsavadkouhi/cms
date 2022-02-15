# Generated by Django 2.2.13 on 2022-02-15 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('centers', '0013_auto_20210905_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpack',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='کد'),
        ),
        migrations.AddField(
            model_name='subtask',
            name='weight',
            field=models.IntegerField(default=1, verbose_name='وزن'),
        ),
        migrations.AlterField(
            model_name='project',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='project_manager', to='accounts.Profile', verbose_name='پیمانکار پروژه'),
        ),
        migrations.AlterField(
            model_name='projectpack',
            name='monitoring_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='projectpack_monitoring_manager', to='accounts.Profile', verbose_name='کارشناس کنترل پروژه'),
        ),
    ]
