from datetime import date, datetime

import jdatetime
from django import template

register = template.Library()


@register.filter(expects_localtime=True, is_safe=False)
def j_format_date(value, arg=None):
	"""Formats a date or time according to the given format."""
	if value in (None, ''):
		return ''
	if arg is None:
		# https://docs.python.org/release/2.7.1/library/datetime.html#strftime-and-strptime-behavior
		arg = "%c"
	try:
		if isinstance(value, datetime):
			value = jdatetime.datetime.fromgregorian(datetime=value, locale='fa_IR')
		elif isinstance(value, date):
			value = jdatetime.date.fromgregorian(date=value, locale='fa_IR')
		return value.strftime(arg)
	except AttributeError:
		return ''
