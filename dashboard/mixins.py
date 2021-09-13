from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from .forms import ItemPerPageForm


class PaginatedFilteredListView(ListView):
	# default
	paginate_by = 50
	extra_context = {}

	filter_form_class = None
	filter_form = None
	filter_form_context_object_name = 'filter_form'
	filter_form_initial = None

	# button for this pages before and after current page that will be shown
	pagination_range = 7

	pagination_lower_dot_context_object_name = 'lower_dot'
	pagination_upper_dot_context_object_name = 'upper_dot'
	pagination_range_context_object_name = 'pagination_range'

	per_page_form_class = ItemPerPageForm
	per_page_form = None
	per_page_form_context_object_name = 'per_page_form'

	def get_pagination_range_context(self, paginator, page):
		r_lower = self.pagination_range
		lower_dot = True

		r_upper = self.pagination_range + 1
		upper_dot = True

		if page.number <= self.pagination_range + 1:
			r_lower = page.number - 1
			lower_dot = False

		if page.number + self.pagination_range >= paginator.num_pages:
			r_upper = paginator.num_pages - page.number + 1
			upper_dot = False

		r = [i for i in range(page.number - r_lower, page.number + r_upper)]

		return {
			self.pagination_lower_dot_context_object_name: lower_dot,
			self.pagination_upper_dot_context_object_name: upper_dot,
			self.pagination_range_context_object_name: r
		}

	def get_paginate_by(self, queryset):
		if self.per_page_form_class is not None:
			self.per_page_form = self.per_page_form_class(self.request.GET)
			if self.per_page_form.is_valid():
				paginate_by = self.per_page_form.cleaned_data['per_page']
				if paginate_by != '' and paginate_by is not None:
					self.paginate_by = paginate_by
					# save per page to session, so page change will not effect this
					self.request.session['per_page_item'] = self.paginate_by
				else:
					# no per page submitted, so restore it from session
					self.paginate_by = self.request.session.get('per_page_item', 50)
					self.per_page_form = self.per_page_form_class(initial={'per_page': self.paginate_by})

		return self.paginate_by

	def get_filter_form(self, data=None):
		if self.filter_form_class is None:
			if data is None:
				raise Exception("You have to provide filter_form_class in %s" % self.__class__.__name__)
			return None

		# remove pagination GET data to prevent conflict with filter initials
		local_data = data.copy()
		local_data.pop('page', None)
		local_data.pop('per_page', None)

		if len(local_data) == 0:
			local_data = None
		initial_data = self.get_filter_form_initial()
		self.has_initial = True if initial_data else False
		return self.filter_form_class(local_data, initial=initial_data)

	def get_filter_form_initial(self, ):
		return self.filter_form_initial

	def get_queryset(self):
		self.filter_form = self.get_filter_form(self.request.GET)
		queryset = super().get_queryset()
		if self.filter_form is not None:
			if self.filter_form.is_valid():
				queryset = self.filter_form.get_filter(queryset)
			elif self.has_initial and not self.filter_form.is_bound:
				self.filter_form.cleaned_data = self.filter_form.initial
				queryset = self.filter_form.get_filter(queryset)

		return queryset.distinct()

	def get_context_data(self, *, object_list=None, **kwargs):
		kwargs.update(**self.extra_context)
		context = super().get_context_data(object_list=object_list, **kwargs)

		if self.filter_form is not None:
			context.update(**{
				self.filter_form_context_object_name: self.filter_form,
			})

		if self.per_page_form is not None:
			context.update(**{
				self.per_page_form_context_object_name: self.per_page_form
			})

		paginator = context['paginator']
		if paginator is not None:
			context.update(**self.get_pagination_range_context(paginator, context['page_obj']))

		return context


class RoleMixin(PermissionRequiredMixin):
	permission_required = ()
