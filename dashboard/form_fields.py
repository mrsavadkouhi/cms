from django import forms

from jdatetime import datetime as j_datetime


class JalaiDateTimeField(forms.DateTimeField):

	def to_python(self, value):
		try:
			data = super().to_python(value)

			# return j_datetime.fromgregorian(datetime=data, locale='fa_IR').togregorian()

			date = j_datetime(year=data.year, month=data.month, day=data.day, hour=data.hour, minute=data.minute, second=data.second, tzinfo=data.tzinfo, locale='fa_IR')
			return date.togregorian()
		except:
			return None


class JalaiDateField(forms.DateField):

	def to_python(self, value):
		try:
			data = super().to_python(value)

			# return j_datetime.fromgregorian(datetime=data, locale='fa_IR').togregorian()

			date = j_datetime(year=data.year, month=data.month, day=data.day, tzinfo=data.tzinfo, locale='fa_IR')
			return date.togregorian()
		except:
			return None
