# Generated by Django 2.2.9 on 2021-08-28 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('centers', '0010_auto_20210828_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='time_supplement_days',
            field=models.IntegerField(default=0, verbose_name='روزهای متمم شده'),
        ),
        migrations.AddField(
            model_name='project',
            name='time_supplement_description',
            field=models.TextField(blank=True, null=True, verbose_name='توضیحات متمم زمانی'),
        ),
        migrations.AddField(
            model_name='project',
            name='time_supplemented',
            field=models.BooleanField(default=False, verbose_name='مشمول متمم زمانی شده؟'),
        ),
        migrations.AddField(
            model_name='projectpack',
            name='time_supplement_days',
            field=models.IntegerField(default=0, verbose_name='روزهای متمم شده'),
        ),
        migrations.AddField(
            model_name='projectpack',
            name='time_supplement_description',
            field=models.TextField(blank=True, null=True, verbose_name='توضیحات متمم زمانی'),
        ),
        migrations.AddField(
            model_name='projectpack',
            name='time_supplemented',
            field=models.BooleanField(default=False, verbose_name='مشمول متمم زمانی شده؟'),
        ),
    ]
