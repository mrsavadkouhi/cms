# Generated by Django 2.2.13 on 2021-09-16 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_auto_20210828_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='due_flag',
            field=models.IntegerField(default=False, verbose_name='قابل پرداخت بودن تراکنش'),
        ),
    ]
