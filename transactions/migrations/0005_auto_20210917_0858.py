# Generated by Django 2.2.13 on 2021-09-17 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_transaction_due_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpacktransaction',
            name='due_progress',
            field=models.IntegerField(default=0, verbose_name='موعد وزنی پرداخت'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='موعد پرداخت'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='due_flag',
            field=models.BooleanField(default=False, verbose_name='قابل پرداخت بودن تراکنش'),
        ),
    ]
