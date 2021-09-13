from django import template

register = template.Library()


@register.simple_tag
def has_perms(user, perms):
	perms_list = perms.split(';')
	return user.profile.has_perms(perms_list)


@register.filter(is_safe=True)
def check_user_permission(user, permissions):
	if user.is_superuser:
		return True

	permissions_list = permissions.split(',')
	for p in permissions_list:
		try:
			if getattr(user.profile, "is_" + p):
				return True
		except:
			pass

	return False


@register.filter(is_safe=True)
def in_list_and(main_list, sub_list_str):
	'''
	Check the existence of all of sub_list_str items in main_list
	:param main_list: list or any object that support 'in' command
	:param sub_list_str: a list of items which delimited by ,
	:return: True or False
	'''
	if sub_list_str is None:
		return True
	sub_list = [item.strip() for item in sub_list_str.split(',')]
	return all(item in main_list for item in sub_list)


@register.filter(is_safe=True)
def in_list_or(main_list, sub_list_str):
	'''
	Check the existence one of sub_list_str items in main_list
	:param main_list: list or any object that support 'in' command
	:param sub_list_str: a list of items which delimited by ,
	:return: True or False
	'''
	if sub_list_str is None:
		return True
	sub_list = [item.strip() for item in sub_list_str.split(',')]
	return any(item in main_list for item in sub_list)


@register.filter(is_safe=True)
def check_path(path, locs):
	loc_list = locs.split(',')
	for l in loc_list:
		if l in path:
			return True
	return False


@register.filter
def dash2underline(value):
	return value.replace("-", "_")
