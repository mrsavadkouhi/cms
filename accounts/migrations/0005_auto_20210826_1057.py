# Generated by Django 2.2.9 on 2021-08-26 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20210823_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='code',
            field=models.CharField(choices=[('users', 'مدیریت کاربران'), ('centers', 'مدیریت مراکز'), ('projectpacks', 'مدیریت دسته پروژه ها'), ('projects', 'مدیریت پروژه ها'), ('equipments', 'مدیریت تجهیزات'), ('transactions', 'مدیریت تراکنش ها'), ('center', 'مدیریت مرکز'), ('user', 'مدیریت کاربران مرکز'), ('equipment', 'مدیریت تجهیزات مرکز'), ('transaction', 'مدیریت تراکنش های مرکز'), ('projectpack', 'مدیریت دسته پروژه های مرکز'), ('projectpack_monitoring', 'نظارت دسته پروژه های مرکز'), ('project', 'مدیریت پروژه های مرکز'), ('project_monitoring', 'نظارت پروژه های مرکز')], max_length=30, verbose_name='کد'),
        ),
    ]
