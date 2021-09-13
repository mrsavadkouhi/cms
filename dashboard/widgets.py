from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields, widgets


# read options from "data-dualbox<optionname>" attributes
# list at https://www.virtuosoft.eu/code/bootstrap-duallistbox/
# 'owners': SelectMultiple_DualListBoxWidget(attrs={'data-dualboxinfoTextEmpty': 'Empty list'}),
class SelectMultiple_DualListBoxWidget(widgets.SelectMultiple):
	'''
	This widget has problem with required fields, make sure you add required=False to field, or you will get
	``An invalid form control with name='' is not focusable.`` error on form submit.
	'''
	template_name = 'widgets/select-multiple-dual-lis-box-widget.html'

	class Media:
		# extend = False
		js = (
			'vendors/bootstrap-duallistbox/jquery.bootstrap-duallistbox.js',
		)
		css = {
			'all': ('vendors/bootstrap-duallistbox/bootstrap-duallistbox.min.css',),
		}

	def render(self, name, value, attrs=None, renderer=None):
		final_attrs = self.build_attrs(self.attrs, attrs)
		return super().render(name, value, final_attrs)


class ClearableImageInput(widgets.ClearableFileInput):
	template_name = 'widgets/clearable_image_input.html'


class Chosen(widgets.Widget):
	'''
	This widget has problem with required fields, make sure you add required=False to field, or you will get
	``An invalid form control with name='' is not focusable.`` error on form submit.
	'''
	template_name = 'widgets/select-chosen-widget.html'

	class Media:
		# extend = False
		js = (
			'vendors/chosen/chosen.jquery.min.js',
		)
		css = {
			'all': ('vendors/chosen/chosen.min.css', 'vendors/chosen/bootstrap-chosen.css'),
		}

	def render(self, name, value, attrs=None, renderer=None):
		final_attrs = self.build_attrs(self.attrs, attrs)
		if 'class' in final_attrs:
			final_attrs['class'] += ' chosen-select'
		return super().render(name, value, final_attrs)


class Select_Chosen(Chosen, widgets.Select):
	pass


class SelectMultiple_Chosen(Chosen, widgets.SelectMultiple):
	pass


# https://stackoverflow.com/a/46409022
FILE_INPUT_CONTRADICTION = object()


class ClearableMultipleFilesInput(widgets.ClearableFileInput):
	def value_from_datadict(self, data, files, name):
		upload = files.getlist(name)  # files.get(name) in Django source

		if not self.is_required and widgets.CheckboxInput().value_from_datadict(
				data, files, self.clear_checkbox_name(name)):

			if upload:
				# If the user contradicts themselves (uploads a new file AND
				# checks the "clear" checkbox), we return a unique marker
				# objects that FileField will turn into a ValidationError.
				return FILE_INPUT_CONTRADICTION
			# False signals to clear any existing value, as opposed to just None
			return False
		return upload


class MultipleFilesField(fields.FileField):
	widget = ClearableMultipleFilesInput

	def clean(self, data, initial=None):
		# If the widget got contradictory inputs, we raise a validation error
		if data is FILE_INPUT_CONTRADICTION:
			raise ValidationError(self.error_message['contradiction'], code='contradiction')
		# False means the field value should be cleared; further validation is
		# not needed.
		if data is False:
			if not self.required:
				return False
			# If the field is required, clearing is not possible (the widg    et
			# shouldn't return False data in that case anyway). False is not
			# in self.empty_value; if a False value makes it this far
			# it should be validated from here on out as None (so it will be
			# caught by the required check).
			data = None
		if not data and initial:
			return initial
		return data


class MultipleImageField(fields.ImageField, MultipleFilesField):
	pass


class CustomFormSet(forms.BaseFormSet):

	def get_form_kwargs(self, index):
		if index is not None:
			return self.form_kwargs[index].copy()
		else:
			return self.form_kwargs.copy()


class GroupedModelChoiceIterator(forms.models.ModelChoiceIterator):
	def __iter__(self):
		if self.field.empty_label is not None:
			yield ("", self.field.empty_label)

		from itertools import groupby

		queryset = self.queryset
		# Can't use iterator() when queryset uses prefetch_related()
		if not queryset._prefetch_related_lookups:
			queryset = queryset.iterator()

		for group, choices in groupby(self.queryset.all(), key=lambda row: getattr(row, self.field.group_by_field)):
			if self.field.group_label(group):
				yield (
					self.field.group_label(group),
					[self.choice(ch) for ch in choices]
				)


class GroupedModelChoiceBase():
	iterator = GroupedModelChoiceIterator

	def __init__(self, group_by_field, group_label=None, *args, **kwargs):
		"""
		group_by_field is the name of a field on the model
		group_label is a function to return a label for each choice group
		"""
		super().__init__(*args, **kwargs)
		self.group_by_field = group_by_field
		if group_label is None:
			self.group_label = lambda group: group
		else:
			self.group_label = group_label


class GroupedModelChoiceField(GroupedModelChoiceBase, forms.ModelChoiceField):
	pass


class GroupedModelMultiChoiceField(GroupedModelChoiceBase, forms.ModelMultipleChoiceField):
	pass


class JSTreeMultiple(widgets.CheckboxSelectMultiple):
	template_name = 'widgets/jstree-widget.html'

	class Media:
		# extend = False
		js = (
			'vendors/jstree/jstree.min.js',
		)
		css = {
			'all': ('vendors/jstree/themes/default/style.min.css',),
		}
