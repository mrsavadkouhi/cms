import datetime

from django.db import models
from django.db.models import Q

from accounts.models import Profile
from centers.models import Center, Project

EQUIPMENT_TYPES = [
    ('car', 'ماشین'),
    ('pc', 'رایانه'),
    ('laptop', 'رایانه همراه'),
    ('tablet', 'تبلت'),
    ('mobile', 'تلفن همراه'),
]


class EquipmentType(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام', unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        return f"{self.name}-{self.description}"


class Equipment(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام', unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    owner = models.ForeignKey(to=Center, on_delete=models.PROTECT, verbose_name='مرکز')
    base_price = models.FloatField(default=0, verbose_name='هزینه( نفر ساعت)')

    type = models.ForeignKey(to=EquipmentType, on_delete=models.PROTECT, verbose_name='نوع')

    is_rented = models.BooleanField(default=False, verbose_name='اجاره؟')

    def __str__(self):
        return f"{self.name}-{self.owner.name}"

    def check_if_out_of_rent(self):
        now = datetime.datetime.now()
        rents = Rent.objects.filter(equipment=self, to__gte=now)
        if rents.count():
            self.is_rented = True
            for rent in rents:
                rent.is_reservation = False
            return False
        self.is_rented = False
        self.save()
        return True


class Rent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    equipment = models.ForeignKey(to=Equipment, on_delete=models.PROTECT, verbose_name='تجهیزات')

    borrower = models.ForeignKey(to=Profile, on_delete=models.PROTECT, verbose_name='اجاره کننده')
    center = models.ForeignKey(to=Center, on_delete=models.PROTECT, verbose_name='مرکز')
    project = models.ForeignKey(to=Project, on_delete=models.PROTECT, verbose_name='پروژه')

    at = models.DateTimeField(verbose_name='شروع قرارداد اجاره')
    to = models.DateTimeField(verbose_name='سررسید قرارداد اجاره')

    reserve_for = models.IntegerField(default=1, verbose_name='اچاره به ازای نفر')

    payment = models.FloatField(default=0, verbose_name='مبلغ قرارداد اجاره')
    paid = models.FloatField(default=0, verbose_name='مبلغ پرداخت شده')

    returned_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ خاتمه قرارداد')

    is_reservation = models.BooleanField(default=True, verbose_name='فرآیند رزرو؟')

    def __str__(self):
        return f"{self.borrower}-{self.center.name}-{self.project.name}"

    @property
    def total_price(self):
        diff = self.to - self.at
        hours = diff.total_seconds() / 3600
        return hours*self.reserve_for*self.equipment.base_price

    @property
    def total_hours(self):
        diff = self.to - self.at
        hours = diff.total_seconds() / 3600
        return hours
