# Generated by Django 2.2.9 on 2021-08-26 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('centers', '0006_auto_20210826_1113'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='center',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='centers.Center', verbose_name='مرکز'),
            preserve_default=False,
        ),
    ]
