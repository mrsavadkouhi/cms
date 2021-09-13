import json
from itertools import chain

from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.db.models import ProtectedError, QuerySet
from django.db.models.base import ModelBase
from django.db.models.fields.files import *
from django.http import HttpResponseNotAllowed, JsonResponse
from django.views import View
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseCreateView, BaseDeleteView, BaseUpdateView, FormMixin
from django.views.generic.list import BaseListView


class JSONResponseMixin(object):
	"""
	This Class is main Json Mixin. the idea of this class comes from
	`More than just HTML <https://docs.djangoproject.com/en/1.11/topics/class-based-views/mixins/#more-than-just-html>`_.

	This class serializes context data and render it as a **JsonResponse**.
	"""

	"""
	Use model fields ``verbose_names`` as key in serialization or field original name
	"""
	use_verbose_names = False

	ignored_context_keys = None
	"""
	Keys that excluded from being rendered to json.
	"""

	model_fields = None
	"""
	If defined, only this fields will be serialized from models
	"""

	def render_to_json_response(self, context, render_pure_context=False, **response_kwargs):
		"""
		Generates data dictionary by using :py:meth:`get_data` and returns **JsonResponse**

		:param dict context: payload of response
		:param render_pure_context: if ``True``, it will render context without any process.
		:param dict response_kwargs: data to be passed to ``JsonResponse``
		:return: HTTP JsonResponse
		:rtype: JsonResponse
		"""
		if render_pure_context:
			return JsonResponse(context, safe=False, **response_kwargs)
		else:
			self.ignored_context_keys = self.get_ignored_context_keys()

			data = self.get_data(context)

			self.remove_duplicate_obj(data)

			return JsonResponse(data, safe=False, **response_kwargs)

	def render_to_response(self, context, **response_kwargs):
		return self.render_to_json_response(context, **response_kwargs)

	def get_data(self, context):
		"""
		Returns the object that will be serialized as JSON in JsonResponse.

		:param dict context: dictionary or list of data, usually output of :py:meth:`get_context_data`
		:return: dictionary of json serializable data
		:rtype: dict
		"""
		obj = None
		if isinstance(context, dict):
			obj = {}
			for key in context:
				if key not in self.ignored_context_keys:
					obj[key] = self.get_instance_data(context[key])
		elif isinstance(context, list):
			obj = []
			for val in context:
				obj.append(self.get_instance_data(val))

		return obj

	def get_instance_data(self, obj):
		"""
		Checks some condition on the object and try to serialize it

		:param obj:
		:return: dictionary or list
		"""
		# Valid JSON types : string, number, boolean
		if isinstance(obj, (int, float, bool, str)) or obj is None:
			return obj

		# This handles dictionaries
		if isinstance(obj, dict):
			return self.get_data(obj)

		# This handles QuerySets and other iterable types
		if not isinstance(obj, str):
			try:
				iterable = iter(obj)
			except TypeError:
				pass
			else:
				return self.get_data(list(iterable))

		# This handles Models
		if isinstance(obj.__class__, ModelBase):
			if hasattr(obj, 'serialize') and callable(getattr(obj, 'serialize')):
				return obj.serialize()
			return self.serialize_model(obj)

		# This handles Paginator
		if isinstance(obj, Paginator):
			page = obj.__dict__
			page.pop("object_list", None)
			return self.get_data(page)

		# Other Python Types:
		try:
			# return force_text(obj)
			return json.dumps(obj)
		except Exception:
			# Last resort:
			return obj

	def serialize_model(self, obj):
		"""
		Serialize database models

		:param model obj: database model object
		:return: dictionary
		:rtype: dict
		"""
		# Add string output of model
		try:
			tmp = {
				'__str': str(obj)
			}
		except:
			tmp = {
				'__str': '--'
			}

		many = [f.name for f in obj._meta.many_to_many]

		# ``class._meta.get_all_field_names()`` has been deprecated in Django 1.10
		# getting all_field_names according to the docs:
		# `migrating from the old api <https://docs.djangoproject.com/en/1.10/ref/models/meta/#migrating-from-the-old-api>`_
		all_field_names = list(set(chain.from_iterable(
			# This two line are if argument
			(field.name, field.attname) if hasattr(field, 'attname') else (field.name,)  # for action
			for field in obj._meta.get_fields()
			# For complete backwards compatibility, you may want to exclude
			# GenericForeignKey from the results.
			# check field is not relation
			if ((field.many_to_one is None) and (field.related_model is None) and (field.one_to_one is None))
		)))

		# add model properties to list
		for property in obj._meta._property_names:
			all_field_names.append(property)

		if self.use_verbose_names:
			all_verbose_names = {n: obj._meta.get_field(n).verbose_name.title() for n in all_field_names}
		else:
			all_verbose_names = {n: n for n in all_field_names}

		for field in all_field_names:
			# get_<field>_display detection and usage for choices fields
			if hasattr(obj, 'get_' + field + '_display'):
				tmp[all_verbose_names[field]] = getattr(obj, 'get_' + field + '_display')()
				continue
			# TODO: check many to many serialize functionality
			if len(many) > 0 and field in many:
				many.remove(field)
				tmp[all_verbose_names[field]] = getattr(obj, field).all()
			elif self.model_fields is None or (self.model_fields is not None and field in self.model_fields):
				attr = getattr(obj, field, None)
				# TODO: check ImageField serialize functionality
				if isinstance(attr, FieldFile) or isinstance(attr, ImageFieldFile):
					try:
						tmp[all_verbose_names[field]] = attr.url
					except:
						tmp[all_verbose_names[field]] = None
				# for jalali date im models
				elif isinstance(attr, datetime.date) or hasattr(attr, 'strftime'):
					tmp[all_verbose_names[field]] = attr.strftime('%Y-%m-%d')
				# For relations
				elif isinstance(attr, QuerySet):
					tmp[all_verbose_names[field]] = self.queryset_serializer(attr, field)
				# one to one
				elif isinstance(attr.__class__, ModelBase):
					if hasattr(attr, 'serialize') and callable(getattr(attr, 'serialize')):
						tmp[all_verbose_names[field]] = attr.serialize()
					tmp[all_verbose_names[field]] = self.serialize_model(attr)
				else:
					tmp[all_verbose_names[field]] = attr
		return tmp

	def get_ignored_context_keys(self):
		"""
		returns value of ignored_context_key

		:return:  ignored_context_key
		:rtype: list
		"""
		if self.ignored_context_keys is None:
			return []
		return self.ignored_context_keys

	def remove_duplicate_obj(self, context, duplicates=None):
		"""
		remove given keys from context if they are duplicated in other keys. also remove **view** key if exists.

		The default value of duplicates is ``["object", "object_list", "page_obj"]``, setting duplicates will be override this.

		:param dict context:
		:param list duplicates: list of probably duplicated keys.
		:return: clear dictionary
		"""
		if duplicates is None:
			duplicates = ["object", "object_list", "page_obj"]
		# Check if the duplicate key is in the context
		for duplicate in duplicates:
			if duplicate in context:
				# Search to ensure that this duplicate is in fact duplicated
				for key, val in context.items():
					if key == duplicate:  # Skip the duplicate object itself
						continue
					if val == context[duplicate]:
						del context[duplicate]
						break

		try:
			context.pop("view", None)
		except:
			pass

		return context

	def queryset_serializer(self, queryset, field_name):
		'''
		:param queryset: The QuerySet Object that will be serialized
		:param field_name: name of the field that contains the queryset, useful for scenarios that need different serializer for different fields
		:return: serialized list
		'''
		serialized_data = []
		for obj in queryset:
			dict = {}
			if (hasattr(obj, 'id')):
				dict['id'] = obj.id
			if (hasattr(obj, 'pk')):
				dict['pk'] = obj.pk
			try:
				dict['__str'] = str(obj)
			except:
				dict['__str'] = ""

			serialized_data.append({dict})
		return serialized_data


class JSONListView(JSONResponseMixin, BaseListView):
	"""
	This View is Json List View.
	Default behavior of this class is like ``ListView``.

	If you want to be sure that the request is an **AJAX** call,
	you should override :py:meth:`get` or :py:meth:`post` and check for that.
	"""
	pass


class JSONDetailView(JSONResponseMixin, BaseDetailView):
	"""
	This View is Json Detail View.
	Default behavior of this class is like ``DetailView``.

	If you want to be sure that the request is an **AJAX** call,
	you should override :py:meth:`get` or :py:meth:`post` and check for that.
	"""
	pass


class JSONDataView(JSONResponseMixin, View):
	"""
	This View is a General-Purpose Json View.
	Default behavior of this class is rendering ``GET`` data as a json.
	You Should override ``get_context_data`` and return a **Dictionary**.

	If you want to be sure that the request is an **AJAX** call,
	you should override :py:meth:`get` or :py:meth:`post` and check for that.
	"""

	def get_context_data(self, **kwargs):
		"""
		returns ``GET`` data to be rendered as JSON.

		:param dict kwargs: GET data,Auto generated.
		:rtype: dict
		"""
		return kwargs

	def get(self, *args, **kwargs):
		"""
		Handles **GET request**. gets data that should be rendered
		from :py:meth:`get_context_data` and returns json response

		:param args:
		:param dict kwargs:
		:rtype: JsonResponse
		"""
		context = self.get_context_data(**kwargs)
		return self.render_to_response(context)

	def render_to_response(self, context, **response_kwargs):
		return self.render_to_json_response(context, render_pure_context=True, **response_kwargs)


class JSONFormMixin(JSONResponseMixin, FormMixin):
	"""
	This is a Form Mixin and handles base functionally of a
	form that is passed as JSON

	.. note::

		Don't forget to pass **CSRF Token** in yor data. Default
		key for that is ``csrfmiddlewaretoken``. Read more at
		`CSRF Docs <https://docs.djangoproject.com/en/1.11/ref/csrf/>`_
	"""
	ignored_context_keys = ['form']
	"""
	Remove **form** key from JSON response
	"""

	def get_form_class(self):
		"""
		There will be issues if form_class is None, so override this
		method to check and see if we have one or not.
		"""
		form_class = super(JSONFormMixin, self).get_form_class()
		if form_class is None:
			raise ImproperlyConfigured(
				"No form class to validate. Please set form_class on"
				" the view or override 'get_form_class()'.")
		return form_class

	def get_success_url(self):
		"""
		Overridden to ensure that JSON data gets returned, rather than HttpResponseRedirect.
		:rtype: None
		"""
		return None

	def form_valid(self, form):
		"""
		Overridden to ensure that an HttpResponseRedirect does not get called with a success_url.
		instead render_to_response some JSON data.

		But make sure to override this method in sub classes and call ``form.save()`` and
		``super().form_valid(form)``
		"""
		return self.render_to_response(self.get_context_data(success=True))

	def form_invalid(self, form):
		"""
		Overridden to ensure that a form object isn't returned, since
		that has some weird serialization issues. Instead pass back
		the errors from the form, and a JSON flag ``success: false``.
		"""
		context = self.get_context_data(success=False)
		context['errors'] = form.errors
		return self.render_to_response(context)

	def get(self, request, *args, **kwargs):
		"""
		Overridden so that on a GET request the response isn't allowed.
		JSON Forms are intrinsically POST driven things, a GET makes
		no sense in the context of a form. (What would you get?). For
		Normal HTTP, you would pass back an empty form, but that's
		pretty useless for JSON. So we pwn this entire method right
		off the bat to ensure no screwiness or excessive net traffic.
		"""
		return HttpResponseNotAllowed(['GET', ])


class JSONCreateView(JSONFormMixin, BaseCreateView):
	def form_valid(self, form):
		"""
		If the form is valid, save the associated model, Then calls
		``super().form_valid(form)`` to return the JSON
		"""
		self.object = form.save()
		return super(JSONCreateView, self).form_valid(form)


class JSONUpdateView(JSONFormMixin, BaseUpdateView):
	def form_valid(self, form):
		"""
		If the form is valid, save the associated model, Then calls
		``super().form_valid(form)`` to return the JSON
		"""
		self.object = form.save()
		return super(JSONUpdateView, self).form_valid(form)


class JSONDeleteView(JSONResponseMixin, BaseDeleteView):
	def delete(self, request, *args, **kwargs):
		"""
		Calls the delete() method on the fetched object and then
		returns a JSON response with ``success : True``.
		"""
		self.object = self.get_object()
		try:
			self.object.delete()
			return self.render_to_response(self.get_context_data(success=True))
		except ProtectedError as err:
			context = self.get_context_data(success=False, error=f'{err}')
			return self.render_to_response(context, status=500, )
