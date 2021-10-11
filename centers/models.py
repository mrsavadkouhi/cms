from datetime import datetime
import time

from polymorphic.models import PolymorphicModel
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile

STATUS_TYPES = [
    ('to_do', 'جهت انجام'),
    ('inprogress', 'در حال انجام'),
    ('completed', 'انجام شده'),
    ('verified', 'تایید شده'),
]

TRANSACTION_TITTLES = [
    ('prepayment', 'پیش پرداخت'),
    ('installment', 'قسط'),
    ('paragraph', 'بند'),
]


class Center(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام', unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    # created_by = models.ForeignKey(to=Profile, on_delete=models.PROTECT, null=True, related_name='center_creator', verbose_name='مدیر ایجاد')

    manager = models.ForeignKey(to=Profile, on_delete=models.PROTECT, related_name='center_manager',
                                verbose_name='مدیر مرکز')
    employees = models.ManyToManyField(to=Profile, blank=True, verbose_name='اعضای مرکز')

    def __str__(self):
        return f"{self.name}-{self.manager}"


def get_projectpack_attachment_directory_path(instance, filename):
    return 'projectpacks/%d_attachment_%s' % (int(time.time()), filename)


class ProjectPackAttachment(models.Model):
    file = models.FileField(upload_to=get_projectpack_attachment_directory_path, verbose_name='فایل', max_length=255)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')


class ProjectPack(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام', unique=True)
    code = models.CharField(null=True, blank=True, max_length=255, verbose_name='کد')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    manager = models.ForeignKey(to=Profile, on_delete=models.PROTECT, related_name='projectpack_manager',
                                verbose_name='مدیر پک پروژه')
    monitoring_manager = models.ForeignKey(to=Profile, on_delete=models.PROTECT, related_name='projectpack_monitoring_manager',
                                verbose_name='کارشناس کنترل پروژه')
    center = models.ForeignKey(to=Center, on_delete=models.PROTECT, verbose_name='مرکز')
    # employees = models.ManyToManyField(to=Profile, blank=True, verbose_name='اعضای پروژه')

    started_at = models.DateTimeField(null=True, blank=True, verbose_name='شروع قرارداد')
    to_be_finished = models.DateTimeField(verbose_name='ددلاین قرارداد')
    # duration = models.FloatField(default=0, verbose_name='مدت قرارداد')

    payment = models.IntegerField(verbose_name='مبلغ قرارداد')
    paid = models.IntegerField(default=0, verbose_name='مبلغ پرداخت شده')
    usable_fund = models.IntegerField(default=0, verbose_name='مبلغ قابل استفاده جهت تسویه پروژه')

    created_financial_statement = models.BooleanField(default=False, verbose_name='صورت مالی ایجاد شده؟')

    time_supplemented = models.BooleanField(default=False, verbose_name='مشمول متمم زمانی شده؟')
    time_supplement_days = models.IntegerField(default=0, verbose_name='روزهای متمم شده')
    time_supplement_description = models.TextField(null=True, blank=True, verbose_name='توضیحات متمم زمانی')
    time_supplement_form_uploaded = models.BooleanField(default=False, verbose_name='فرم متمم زمانی بارگذاری شده؟')

    # progress = models.IntegerField(default=0, verbose_name='درصد پیشرفت وزنی')
    # weightless_progress = models.IntegerField(default=0, verbose_name='درصد پیشرفت')

    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ خاتمه قرارداد')

    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='to_do', verbose_name='وضعیت')

    attachments = models.ManyToManyField(ProjectPackAttachment, blank=True, verbose_name='فایل ها')

    def __str__(self):
        return f"{self.name}-{self.status}"

    def check_if_completed(self):
        for project in self.project_set.all():
            if project.status != 'completed':
                return False
        self.status = 'completed'
        self.save(update_fields=['status'])
        return True

    def check_if_verified(self):
        for project in self.project_set.all():
            if project.status != 'verified':
                return False
        self.status = 'verified'
        self.save(update_fields=['status'])
        return True


@receiver(post_save, sender=ProjectPack, dispatch_uid="projectpack_status_update")
def change_status(sender, instance, created, raw, update_fields, **kwargs):
    try:
        # create new log for new items
        if created:
            pass
        elif 'status' in update_fields:
            if instance.status == 'inprogress':
                instance.started_at = datetime.now()
                instance.finished_at = None
            elif instance.status == 'completed':
                instance.finished_at = None
            elif instance.status == 'to_do':
                instance.finished_at = None
            elif instance.status == 'verified':
                instance.finished_at = datetime.now()
            instance.save()
    except Exception:
        pass


def get_project_attachment_directory_path(instance, filename):
    return 'projects/%d_attachment_%s' % (int(time.time()), filename)


class ProjectAttachment(models.Model):
    file = models.FileField(upload_to=get_project_attachment_directory_path, verbose_name='فایل', max_length=255)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')


class Project(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام', unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    manager = models.ForeignKey(to=Profile, on_delete=models.PROTECT, related_name='project_manager',
                                verbose_name='پیمانکار پروژه')
    monitoring_manager = models.ForeignKey(to=Profile, on_delete=models.PROTECT, related_name='project_monitoring_manager',
                                verbose_name='ناظر پروژه')
    center = models.ForeignKey(to=Center, on_delete=models.PROTECT, verbose_name='مرکز')
    project_pack = models.ForeignKey(to=ProjectPack, on_delete=models.PROTECT, verbose_name='پک پروژه')
    employees = models.ManyToManyField(to=Profile, blank=True, related_name='project_employees', verbose_name='اعضای پروژه')

    started_at = models.DateTimeField(null=True, blank=True, verbose_name='شروع قرارداد')
    to_be_finished = models.DateTimeField(verbose_name='ددلاین قرارداد')

    payment = models.IntegerField(verbose_name='مبلغ قرارداد')
    paid = models.IntegerField(default=0, verbose_name='مبلغ پرداخت شده')
    usable_fund = models.IntegerField(default=0, verbose_name='مبلغ قابل استفاده جهت تسویه تسک')

    created_financial_statement = models.BooleanField(default=False, verbose_name='صورت مالی ایجاد شده؟')

    time_supplemented = models.BooleanField(default=False, verbose_name='مشمول متمم زمانی شده؟')
    time_supplement_days = models.IntegerField(default=0, verbose_name='روزهای متمم شده')
    time_supplement_description = models.TextField(null=True, blank=True, verbose_name='توضیحات متمم زمانی')
    time_supplement_form_uploaded = models.BooleanField(default=False, verbose_name='فرم متمم زمانی بارگذاری شده؟')

    progress = models.IntegerField(default=0, verbose_name='درصد پیشرفت وزنی')
    weightless_progress = models.IntegerField(default=0, verbose_name='درصد پیشرفت')

    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ خاتمه قرارداد')

    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='to_do', verbose_name='وضعیت')

    attachments = models.ManyToManyField(ProjectAttachment, blank=True, verbose_name='فایل ها')

    def __str__(self):
        return f"{self.name}-{self.status}"

    def check_if_completed(self):
        for task in self.task_set.all():
            if task.status != 'completed':
                return False
        self.status = 'completed'
        self.save(update_fields=['status'])
        return True

    def check_if_verified(self):
        for task in self.task_set.all():
            if task.status != 'verified':
                return False
        self.status = 'verified'
        self.save(update_fields=['status'])
        return True

    def recalculate_weightless_progress(self):
        to_do = 0
        for task in self.task_set.filter(status='to_do'):
            to_do += 1
        inprogress = 0
        for task in self.task_set.filter(status='inprogress'):
            inprogress += 1
        completed = 0
        for task in self.task_set.filter(status='completed'):
            completed += 1
        verified = 0
        for task in self.task_set.filter(status='verified'):
            verified += 1

        total_task = to_do + inprogress + completed + verified

        if total_task == 0:
            self.weightless_progress = 0
        else:
            self.weightless_progress = round(100 * (verified+completed) / total_task,2)
        self.save()

    def recalculate_progress(self):
        to_do = 0
        for task in self.task_set.filter(status='to_do'):
            to_do += task.weight
        inprogress = 0
        for task in self.task_set.filter(status='inprogress'):
            inprogress += task.weight
        completed = 0
        for task in self.task_set.filter(status='completed'):
            completed += task.weight
        verified = 0
        for task in self.task_set.filter(status='verified'):
            verified += task.weight

        total_task = to_do + inprogress + completed + verified

        if total_task == 0:
            self.progress = 0
        else:
            self.progress = round(100 * (verified+completed) / total_task, 2)
        self.save()


@receiver(post_save, sender=Project, dispatch_uid="project_status_update")
def change_status(sender, instance, created, raw, update_fields, **kwargs):
    try:
        # create new log for new items
        if created:
            pass
        elif 'status' in update_fields:
            if instance.status == 'inprogress':
                instance.started_at = datetime.now()
                instance.finished_at = None
            elif instance.status == 'completed':
                instance.finished_at = None
            elif instance.status == 'to_do':
                instance.finished_at = None
            elif instance.status == 'verified':
                instance.finished_at = datetime.now()
            instance.save()
    except Exception:
        pass


def get_task_attachment_directory_path(instance, filename):
    return 'tasks/%d_attachment_%s' % (int(time.time()), filename)


class TaskAttachment(models.Model):
    file = models.FileField(upload_to=get_task_attachment_directory_path, verbose_name='فایل', max_length=255)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')


class Task(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام', unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    employee = models.ForeignKey(null=True, blank=True, to=Profile, on_delete=models.PROTECT,
                                 related_name='task_employee', verbose_name='کارمند')
    project = models.ForeignKey(null=True, blank=True, to=Project, on_delete=models.PROTECT, verbose_name='پروژه')

    started_at = models.DateTimeField(null=True, blank=True, verbose_name='شروع قرارداد')
    to_be_finished = models.DateTimeField(null=True, blank=True, verbose_name='ددلاین قرارداد')
    # duration = models.FloatField(default=0, verbose_name='مدت قرارداد')

    payment = models.IntegerField(default=0, verbose_name='مبلغ قرارداد')
    paid = models.IntegerField(default=0, verbose_name='مبلغ پرداخت شده')

    created_financial_statement = models.BooleanField(default=False, verbose_name='صورت مالی ایجاد شده؟')

    weight = models.IntegerField(default=1, verbose_name='وزن')

    progress = models.IntegerField(default=0, verbose_name='درصد پیشرفت')

    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ خاتمه قرارداد')

    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='to_do', verbose_name='وضعیت')

    attachments = models.ManyToManyField(TaskAttachment, blank=True, verbose_name='فایل ها')

    def __str__(self):
        return f"{self.name}-{self.project.name}-{self.status}"

    def check_if_completed(self):
        for task in self.subtask_set.all():
            if task.status != 'completed':
                return False
        self.status = 'completed'
        self.save(update_fields=['status'])
        return True

    def check_if_verified(self):
        for task in self.subtask_set.all():
            if task.status != 'verified':
                return False
        self.status = 'verified'
        self.save(update_fields=['status'])
        return True

    def recalculate_progress(self):
        to_do = 0
        for subtask in self.subtask_set.filter(status='to_do'):
            to_do += subtask.weight
        inprogress = 0
        for subtask in self.subtask_set.filter(status='inprogress'):
            inprogress += subtask.weight
        completed = 0
        for subtask in self.subtask_set.filter(status='completed'):
            completed += subtask.weight
        verified = 0
        for subtask in self.subtask_set.filter(status='verified'):
            verified += subtask.weight

        total_subtask = to_do + inprogress + completed + verified

        if total_subtask == 0:
            self.progress = 0
        else:
            self.progress = round(100 * (verified+completed) / total_subtask, 2)
        self.save()


@receiver(post_save, sender=Task, dispatch_uid="task_status_update")
def task_change_status(sender, instance, created, raw, update_fields, **kwargs):
    try:
        # create new log for new items
        if created:
            pass
        elif 'status' in update_fields:
            if instance.status == 'to_do':
                instance.finished_at = None
            elif instance.status == 'inprogress':
                instance.finished_at = None
                if not instance.started_at:
                    instance.started_at = datetime.now()
                instance.project.status = 'inprogress'
                instance.project.save(update_fields=['status'])
            elif instance.status == 'completed':
                instance.finished_at = None
                instance.project.check_if_completed()
            elif instance.status == 'verified':
                instance.finished_at = datetime.now()
                instance.project.check_if_verified()

            instance.save()
    except Exception:
        pass


def get_subtask_attachment_directory_path(instance, filename):
    return 'subtasks/%d_attachment_%s' % (int(time.time()), filename)


class SubTaskAttachment(models.Model):
    file = models.FileField(upload_to=get_subtask_attachment_directory_path, verbose_name='فایل', max_length=255)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')


class SubTask(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام', unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    # created_by = models.ForeignKey(to=Profile, on_delete=models.PROTECT, null=True,related_name='subtask_creator', verbose_name='مدیر ایجاد')

    employee = models.ForeignKey(null=True, blank=True, to=Profile, on_delete=models.PROTECT,
                                 related_name='subtask_employee', verbose_name='مسئول تسک')
    task = models.ForeignKey(to=Task, on_delete=models.PROTECT, verbose_name='تسک')

    started_at = models.DateTimeField(null=True, blank=True, verbose_name='شروع قرارداد')
    to_be_finished = models.DateTimeField(null=True, blank=True, verbose_name='ددلاین قرارداد')
    # duration = models.FloatField(default=0, verbose_name='مدت قرارداد')

    weight = models.IntegerField(default=1, verbose_name='وزن')

    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ خاتمه قرارداد')

    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='to_do', verbose_name='وضعیت')

    attachments = models.ManyToManyField(SubTaskAttachment,blank=True, verbose_name='فایل ها')

    def __str__(self):
        return f"{self.name}-{self.task.name}-{self.task.project.name}-{self.status}"


@receiver(post_save, sender=SubTask, dispatch_uid="subtask_status_update")
def subtask_change_status(sender, instance, created, raw, update_fields, **kwargs):
    try:
        # create new log for new items
        if created:
            pass
        elif 'status' in update_fields:
            if instance.status == 'to_do':
                instance.finished_at = None
            elif instance.status == 'inprogress':
                instance.finished_at = None
                if not instance.started_at:
                    instance.started_at = datetime.now()
                instance.task.status = 'inprogress'
                instance.task.save(update_fields=['status'])
                instance.task.recalculate_progress()
            elif instance.status == 'completed':
                instance.finished_at = None
                instance.task.check_if_completed()
                instance.task.recalculate_progress()
            elif instance.status == 'verified':
                instance.finished_at = datetime.now()
                instance.task.check_if_verified()
                instance.task.recalculate_progress()

            instance.save()
    except Exception:
        pass