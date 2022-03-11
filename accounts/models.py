import time
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse
from phone_field import PhoneField

UNINVERSITIES = [
    ('Sharif', 'دانشگاه صنعتی شریف'),
    ('Tehran', 'دانشگاه تهران'),
    ('Elmos', 'دانشگاه علم و صنعت ایران'),
    ('Amirkabir', 'دانشگاه صنعتی امیرکبیر'),
    ('Beheshti', 'دانشگاه شهید بهشتی'),
    ('Public', 'دانشگاه سراسری'),
    ('Azad', 'دانشگاه آزاد'),
    ('Pyam', 'دانشگاه پیام نور'),
    ('Privte', 'دانشگاه غیر انتفاعی'),
]

SEXES = [
    ('man', 'مرد'),
    ('woman', 'زن'),
]

DEGREES = [
    ('diploma', 'دیپلم'),
    ('bachelor', 'کارشناسی'),
    ('master', 'ارشد'),
    ('phd', 'دکتری'),
]

LANGS = [
    ('C', 'C'),
    ('Python', 'Python'),
    ('Java', 'Java'),
    ('C++', 'C++'),
    ('Django', 'Django'),
    ('Laravel', 'Laravel'),
    ('GO', 'GO'),
]

SOFTWARES = [
    ('cat', 'اتوکد'),
    ('photoshop', 'فتوشاپ'),
    ('corel', 'کرل'),
    ('indesign', 'ایندیزاین'),
    ('catia', 'کتیا'),
]

MEASURES = [
    ('software', 'نرم افزار'),
    ('electronic', 'الکترونیک'),
    ('mechanic', 'مکانیک'),
    ('control', 'کنترل'),
    ('civil', 'عمران'),
]

PERMISSIONS = [
    ('users', 'مدیریت کاربران'),
    ('centers', 'مدیریت مراکز'),
    ('projectpacks', 'مدیریت دسته پروژه ها'),
    ('projects', 'مدیریت پروژه ها'),
    ('equipments', 'مدیریت تجهیزات'),
    ('transactions', 'مدیریت تراکنش ها'),
    #
    ('center', 'مدیریت مرکز'),
    ('user', 'مدیریت کاربران مرکز'),
    ('equipment', 'مدیریت تجهیزات مرکز'),
    ('transaction', 'مدیریت تراکنش های مرکز'),
    ('projectpack', 'مدیریت دسته پروژه های مرکز'),
    ('projectpack_monitoring', 'کارشناس کنترل پروژه های مرکز'),
    ('project', 'پیمانکار پروژه های مرکز'),
    ('project_monitoring', 'نظارت پروژه های مرکز'),
]


def get_avatar_directory_path(instance, filename):
    return 'users/%d_avatar_%s' % (int(time.time()), filename)


def get_resume_directory_path(instance, filename):
    return 'users/%d_resume_%s' % (int(time.time()), filename)


class Lang(models.Model):
    name = models.CharField(max_length=20, choices=LANGS, default='Python', verbose_name='زبان برنامه نویسی')

    def __str__(self):
        return self.name


class Software(models.Model):
    name = models.CharField(max_length=20, choices=SOFTWARES, default='photoshop', verbose_name='نرم افزارهای تخصصی')

    def __str__(self):
        return self.name


class Permission(models.Model):
    code = models.CharField(max_length=30, choices=PERMISSIONS, verbose_name='کد')

    def __str__(self):
        return self.code


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='کاربر')
    avatar = models.ImageField(upload_to=get_avatar_directory_path, verbose_name='Avatar', max_length=255, blank=True,
                               null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    permissions = models.ManyToManyField(to=Permission, blank=True, verbose_name='دسترسی ها')

    mobile_number = models.CharField(max_length=11, verbose_name='تلفن همراه', unique=True)
    phone_number = models.CharField(max_length=20, default='', blank=True, verbose_name='تلفن ثابت')
    address = models.TextField(default='', blank=True, verbose_name='نشانی')

    sex = models.CharField(max_length=20, blank=True, choices=SEXES, default='man', verbose_name='جنسیت')
    degree = models.CharField(max_length=20, blank=True, choices=DEGREES, default='bachelor', verbose_name='مدرک')
    measure = models.CharField(max_length=20, blank=True, choices=MEASURES, default='software', verbose_name='رشته')
    university = models.CharField(max_length=20, blank=True, choices=UNINVERSITIES, default='Public', verbose_name='دانشگاه')
    langs = models.ManyToManyField(to=Lang, blank=True, verbose_name='زبان های برنامه نویسی')
    softwares = models.ManyToManyField(to=Software, blank=True, verbose_name='نرم افزارهای مسلط')
    other_abilities = models.TextField(default='', blank=True, verbose_name='سایر توانایی ها')

    resume = models.FileField(upload_to=get_resume_directory_path, verbose_name='رزومه', max_length=255, blank=True,
                               null=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        try:
            return self.user.get_full_name()
        except:
            return f'profile {self.id}'

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def get_user_center(self):
        center = self.center_set.first()
        return center.id

    @property
    def get_user_center_display(self):
        center = self.center_set.first()
        return center.name

    @property
    def get_user_main_role_display(self):
        main_role = self.permissions.all().first()
        if main_role:
            return main_role.get_code_display()
        return 'عضو مرکز'

    @property
    def has_no_perms(self):
        if self.permissions.all().count():
            return False
        return True

    def has_perms(self, perms):
        if self.permissions.filter(code__in=perms).count():
            return True
        return False

    def get_absolute_url(self):
        return reverse('accounts:profile_details', kwargs={'pk': self.id})


@receiver(pre_save, sender=Profile, dispatch_uid="delete_old_avatar_image_before_save")
def delete_old_avatar_image(sender, instance, raw, update_fields, **kwargs):
    try:
        obj = Profile.objects.get(id=instance.id)
        if obj.avatar != instance.avatar:
            obj.avatar.delete(save=False)
    except Exception:
        pass


@receiver(pre_delete, sender=Profile, dispatch_uid='delete_avatar_file_on_object_delete')
def delete_avatar_media(sender, instance, using, **kwargs):
    instance.avatar.delete(save=False)
