# Generated by Django 2.2.13 on 2021-10-11 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_auto_20210917_0858'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projecttransaction',
            name='due_progress',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='due_date',
        ),
        migrations.AddField(
            model_name='transaction',
            name='due_progress',
            field=models.IntegerField(default=0, verbose_name='موعد وزنی پرداخت'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='tittle',
            field=models.CharField(choices=[('prepayment', 'پیش پرداخت'), ('instalment', 'قسط'), ('paragraph', 'بند'), ('final_instalment', 'حسن انجام کار')], max_length=20, verbose_name='نوع'),
        ),
    ]