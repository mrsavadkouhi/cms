from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import UploadedFile
from django.utils.datastructures import MultiValueDict
from formtools.wizard.storage import NoFileStorageConfigured
from formtools.wizard.storage.session import SessionStorage
from formtools.wizard.views import SessionWizardView


# https://stackoverflow.com/a/46409022/4731038
class CustomSessionStorage(SessionStorage):

	def get_step_files(self, step):
		wizard_files = self.data[self.step_files_key].get(step, {})

		if wizard_files and not self.file_storage:
			raise NoFileStorageConfigured(
				"You need to define 'file_storage' in your "
				"wizard view in order to handle file uploads.")

		if isinstance(wizard_files, MultiValueDict):
			wizard_file_list = []
			for f in wizard_files:
				flist = wizard_files.getlist(f)
				wizard_file_list.append((f, flist))
		else:
			wizard_file_list = iter(wizard_files.items())

		files = MultiValueDict()
		for field, field_dict_list in wizard_file_list:
			if isinstance(field_dict_list, list):
				file_list = []
				for field_dict in field_dict_list:
					field_dict = field_dict.copy()
					tmp_name = field_dict.pop('tmp_name')
					file_list.append(UploadedFile(file=self.file_storage.open(tmp_name), **field_dict))

				if (step, field) not in self._files:
					self._files[(step, field)] = file_list
				files.setlist(field, self._files[(step, field)])
			else:
				field_dict = field_dict_list.copy()
				tmp_name = field_dict.pop('tmp_name')
				if (step, field) not in self._files:
					self._files[(step, field)] = UploadedFile(file=self.file_storage.open(tmp_name), **field_dict)
				files[field] = self._files[(step, field)]

		return files or None

	def set_step_files(self, step, files):
		if files and not self.file_storage:
			raise NoFileStorageConfigured(
				"You need to define 'file_storage' in your "
				"wizard view in order to handle file uploads.")

		if step not in self.data[self.step_files_key]:
			self.data[self.step_files_key][step] = {}

		files = files or {}
		if isinstance(files, MultiValueDict):
			file_list = []
			for f in files:
				flist = files.getlist(f)
				file_list.append((f, flist))
		else:
			file_list = files.items()
		for field, field_file_list in file_list:
			if isinstance(field_file_list, list):
				dict_list = []
				for field_file in field_file_list:
					tmp_filename = self.file_storage.save(field_file.name, field_file)
					file_dict = {
						'tmp_name': tmp_filename,
						'name': field_file.name,
						'content_type': field_file.content_type,
						'size': field_file.size,
						'charset': field_file.charset
					}
					dict_list.append(file_dict)
				self.data[self.step_files_key][step][field] = dict_list
			else:
				tmp_filename = self.file_storage.save(field_file_list.name, field_file_list)
				file_dict = {
					'tmp_name': tmp_filename,
					'name': field_file_list.name,
					'content_type': field_file_list.content_type,
					'size': field_file_list.size,
					'charset': field_file_list.charset
				}
				self.data[self.step_files_key][step][field] = file_dict

	def reset(self):
		# Store unused temporary file names in order to delete them
		# at the end of the response cycle through a callback attached in
		# `update_response`.
		wizard_files = self.data[self.step_files_key]
		for step_files in wizard_files.values():
			for step_file in step_files.values():
				if isinstance(step_file, list):
					for file in step_file:
						self._tmp_files.append(file['tmp_name'])
				else:
					self._tmp_files.append(step_file['tmp_name'])
		self.init_data()

	def update_response(self, response):
		def post_render_callback(response):
			if isinstance(self._files, dict):
				for file_list in self._files.values():
					for file in file_list:
						if not file.closed:
							file.close()
			else:
				for file in self._files.values():
					if not file.closed:
						file.close()

			for tmp_file in self._tmp_files:
				self.file_storage.delete(tmp_file)

		if hasattr(response, 'render'):
			response.add_post_render_callback(post_render_callback)
		else:
			post_render_callback(response)


class CustomSessionWizardView(SessionWizardView):
	storage_name = 'main.wizard_customization.CustomSessionStorage'

	template_list = None

	def get_template_names(self):
		if self.template_name is None and self.template_list is None:
			raise ImproperlyConfigured(
				"CustomSessionWizardView requires either a definition of "
				"'template_name' or 'template_list' or an implementation of 'get_template_names()'")
		if self.template_name is None:
			return [self.template_name]

		return [self.template_list[self.steps.current]]

	def get_form_prefix(self, step=None, form=None):
		if hasattr(self, 'get_form_prefix_%s' % step):
			prefix = getattr(self, 'get_form_prefix_%s' % step)(form)
			return prefix
		return super().get_form_prefix(step)

	def get_form_initial(self, step):
		if hasattr(self, 'get_form_initial_%s' % step):
			init = getattr(self, 'get_form_initial_%s' % step)()
			return init
		return super().get_form_initial(step)

	def get_form_instance(self, step):
		if hasattr(self, 'get_form_instance_%s' % step):
			instance = getattr(self, 'get_form_instance_%s' % step)()
			return instance
		return super().get_form_instance(step)

	def get_form_kwargs(self, step=None):
		if hasattr(self, 'get_form_kwargs_%s' % step):
			kwargs = getattr(self, 'get_form_kwargs_%s' % step)()
			return kwargs
		return super().get_form_kwargs(step)
