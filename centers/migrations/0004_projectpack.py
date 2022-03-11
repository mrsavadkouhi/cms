# Generated by Django 2.2.9 on 2021-08-21 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('centers', '0003_auto_20210821_1327'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectPack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='نام')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='شروع قرارداد')),
                ('to_be_finished', models.DateTimeField(verbose_name='سررسید قرارداد')),
                ('payment', models.IntegerField(verbose_name='مبلغ قرارداد')),
                ('paid', models.IntegerField(default=0, verbose_name='مبلغ پرداخت شده')),
                ('finished_at', models.DateTimeField(blank=True, null=True, verbose_name='تاریخ خاتمه قرارداد')),
                ('status', models.CharField(choices=[('to_do', 'جهت انجام'), ('inprogress', 'در حال انجام'), ('completed', 'انجام شده'), ('verified', 'تایید شده')], default='to_do', max_length=20, verbose_name='وضعیت')),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='centers.Center', verbose_name='مرکز')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='projectpack_manager', to='accounts.Profile', verbose_name='مدیر دسته پروژه')),
                ('monitoring_manager', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='projectpack_monitoring_manager', to='accounts.Profile', verbose_name='ناظر دسته پروژه')),
            ],
        ),
    ]
