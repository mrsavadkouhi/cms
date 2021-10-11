from datetime import datetime
import time

from polymorphic.models import PolymorphicModel
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile
from centers.models import ProjectPack, Project, Task, Center

STATUS_TYPES = [
    ('to_do', 'جهت انجام'),
    ('inprogress', 'در حال انجام'),
    ('completed', 'انجام شده'),
    ('verified', 'تایید شده'),
]

TRANSACTION_TITTLES = [
    ('prepayment', 'پیش پرداخت'),
    ('instalment', 'قسط'),
    ('paragraph', 'بند'),
    ('final_instalment', 'حسن انجام کار'),
]


def get_transaction_attachment_directory_path(instance, filename):
    return 'transactions/%d_attachment_%s' % (int(time.time()), filename)


class TransactionAttachment(models.Model):
    file = models.FileField(upload_to=get_transaction_attachment_directory_path, verbose_name='فایل', max_length=255)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')


class Transaction(PolymorphicModel):
    tittle = models.CharField(max_length=20, choices=TRANSACTION_TITTLES, verbose_name='نوع')

    center = models.ForeignKey(to=Center, on_delete=models.PROTECT, verbose_name='مرکز')

    value = models.IntegerField(default=0, verbose_name='مبلغ تراکنش')

    sequence_number = models.IntegerField(default=0, verbose_name='شماره توالی تراکنش')

    due_flag = models.BooleanField(default=False, verbose_name='قابل پرداخت بودن تراکنش')

    # due_date = models.DateTimeField(null=True, blank=True,verbose_name='موعد پرداخت')
    due_progress = models.IntegerField(default=0, verbose_name='موعد وزنی پرداخت')

    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت شده')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    attachments = models.ManyToManyField(TransactionAttachment, blank=True, verbose_name='فایل ها')


class ProjectPackTransaction(Transaction):
    project_pack = models.ForeignKey(to=ProjectPack, on_delete=models.PROTECT, verbose_name='پک پروژه')


class ProjectTransaction(Transaction):
    project = models.ForeignKey(to=Project, on_delete=models.PROTECT, verbose_name='پروژه')


class TaskTransaction(Transaction):
    task = models.ForeignKey(to=Task, on_delete=models.PROTECT, verbose_name='تسک')