from django import forms
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from centers.models import Center
from dashboard.widgets import Select_Chosen, SelectMultiple_DualListBoxWidget
from .models import Profile, Lang, Software, Permission
import re
from langdetect import detect


# ========  Profile ========
class ProfileCreateForm(forms.ModelForm):
	username = forms.CharField(label='نام کاربری', required=True, error_messages={'required': 'وارد کردن نام کاربری الزامی است.'})
	first_name = forms.CharField(label='نام', required=True,error_messages={'required': 'وارد کردن نام الزامی است.'})
	last_name = forms.CharField(label='نام خانوادگی', required=True,error_messages={'required': 'وارد کردن نام خانوادگی الزامی است.'})
	# role = forms.CharField(label='نقش', required=True, error_messages={'required': 'انتخاب نقش الزامی است.'})
	password = forms.CharField(label='پسورد', required=True, error_messages={'required': 'وارد کردن پسورد الزامی است.'})
	mobile_number = forms.CharField(label='پسورد', required=True, error_messages={'required': 'وارد کردن شماره همراه الزامی است.'})
	email = forms.EmailField(label='ایمیل', required=True, error_messages={'required': 'وارد کردن ایمیل الزامی است.'})
	avatar = forms.ImageField(label='Avatar', required=False)
	resume = forms.FileField(label='Resume', required=False)
	center = forms.ModelChoiceField(label='مرکز', queryset=Center.objects.all(), error_messages={'required': 'انتخاب مرکز الزامی است.'})
	langs = forms.ModelMultipleChoiceField(queryset=Lang.objects.all(), required=False)
	softwares = forms.ModelMultipleChoiceField(queryset=Software.objects.all(), required=False)
	permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False)

	field_order = ['username','first_name', 'last_name','password', 'email', 'mobile_number','avatar', 'resume', 'center', 'sex'
				   ,'degree','university','measure','langs','softwares','permissions','other_abilities']

	class Meta:
		model = Profile
		exclude = ['user', ]

	def clean(self):
		cleaned_data = super().clean()

		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		mobile_number = cleaned_data.get('mobile_number')

		if username:
			if re.search("[ا-ی]", username):
				raise forms.ValidationError("برای نام کاربری از کاراکترهای انگلیسی استفاده نمایید.")
			if User.objects.filter(username=username).exists():
				raise forms.ValidationError("نام کاربری از قبل وجود داشته است.")
			elif re.search("\s", username):
				raise forms.ValidationError("نام کاربری نباید شامل فاصله باشد.")

		if password:
			if re.search("[ا-ی]", password):
				raise forms.ValidationError("برای کلمه عبور از کاراکترهای انگلیسی استفاده نمایید.")
			elif len(password) < 8:
				raise forms.ValidationError("پسورد باید حداقل ۸ کاراکتر باشد.")
			elif not re.search("[a-z]", password):
				raise forms.ValidationError("پسورد باید شامل حروف کوچک باشد.")
			elif not re.search("[A-Z]", password):
				raise forms.ValidationError("پسورد باید شامل حروف بزرگ باشد.")
			elif not re.search("[0-9]", password):
				raise forms.ValidationError("پسورد باید شامل عدد باشد.")
			elif re.search("\s", password):
				raise forms.ValidationError("پسورد نباید شامل فاصله باشد.")

		if mobile_number:
			if not re.search("^09\d{9}$", mobile_number):
				raise forms.ValidationError("لطفا شماره همراه را طبق فرمت *********09 وارد نمایید.")

		return cleaned_data

	def save(self, commit=True):
		instance = super().save(commit=False)
		user = User.objects.create_user(username=self.cleaned_data['username'], email=self.cleaned_data['email'],
										password=self.cleaned_data['password'],
										first_name=self.cleaned_data['first_name'],
										last_name=self.cleaned_data['last_name'], )

		instance.user = user
		self.instance = instance
		if commit:
			# If committing, save the instance and the m2m data immediately.
			self.instance.save()
			self._save_m2m()

		center = self.cleaned_data["center"]
		center.employees.add(self.instance)
		default_center = Center.objects.get(name='مرکز پیشفرض')
		if center == default_center:
			pass
		elif self.instance in default_center.employees.all():
			default_center.employees.remove(self.instance)

		return self.instance


class ProfileUpdateForm(forms.ModelForm):
	first_name = forms.CharField(label='نام', required=False)
	last_name = forms.CharField(label='نام خانوادگی', required=False)
	# password = forms.CharField(label='پسورد', required=True)
	email = forms.EmailField(label='ایمیل', required=True)
	avatar = forms.ImageField(label='Avatar', required=False)
	resume = forms.ImageField(label='Resume', required=False)
	center = forms.ModelChoiceField(label='مرکز', queryset=Center.objects.all(), required=True)
	langs = forms.ModelMultipleChoiceField(queryset=Lang.objects.all(), required=False)
	softwares = forms.ModelMultipleChoiceField(queryset=Software.objects.all(), required=False)
	permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False)

	field_order = ['username','first_name', 'last_name', 'email', 'avatar', 'resume', 'center', 'sex'
				   ,'degree','university','measure','langs','softwares','permissions','other_abilities']

	class Meta:
		model = Profile
		exclude = ['user', ]

	def __init__(self, *args, **kwargs):
		initial = kwargs.get('initial', {})
		instance = kwargs.get('instance', None)
		if instance is not None:
			initial['first_name'] = instance.user.first_name
			initial['last_name'] = instance.user.last_name
			initial['email'] = instance.user.email

		kwargs['initial'] = initial
		super().__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super().clean()

		# password = cleaned_data.get('password')
		mobile_number = cleaned_data.get('mobile_number')

		# if password:
		# 	if re.search("[ا-ی]", password):
		# 		raise forms.ValidationError("برای کلمه عبور از کاراکترهای انگلیسی استفاده نمایید.")
		# 	elif len(password) < 8:
		# 		raise forms.ValidationError("پسورد باید حداقل ۸ کاراکتر باشد.")
		# 	elif not re.search("[a-z]", password):
		# 		raise forms.ValidationError("پسورد باید شامل حروف کوچک باشد.")
		# 	elif not re.search("[A-Z]", password):
		# 		raise forms.ValidationError("پسورد باید شامل حروف بزرگ باشد.")
		# 	elif not re.search("[0-9]", password):
		# 		raise forms.ValidationError("پسورد باید شامل عدد باشد.")
		# 	elif re.search("\s", password):
		# 		raise forms.ValidationError("پسورد نباید شامل فاصله باشد.")

		if mobile_number:
			if not re.search("^09\d{9}$", mobile_number):
				raise forms.ValidationError("لطفا شماره همراه را طبق فرمت *********09 وارد نمایید.")

		return cleaned_data

	def save(self, commit=True):
		instance = super().save(commit=False)

		instance.user.first_name = self.cleaned_data['first_name']
		instance.user.last_name = self.cleaned_data['last_name']
		instance.user.email = self.cleaned_data['email']

		# if self.cleaned_data['password']:
		# 	instance.user.set_password(self.cleaned_data['password'])

		self.instance = instance
		if commit:
			# If committing, save the instance and the m2m data immediately.
			instance.user.save()
			self.instance.save()
			self._save_m2m()

		center = self.cleaned_data["center"]
		center.employees.add(self.instance)
		default_center = Center.objects.get(name='مرکز پیشفرض')
		if center == default_center:
			pass
		elif self.instance in default_center.employees.all():
			default_center.employees.remove(self.instance)

		return self.instance
