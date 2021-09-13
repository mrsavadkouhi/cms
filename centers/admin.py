from django.contrib import admin

from .models import Project, Task, SubTask, Center, TaskAttachment, SubTaskAttachment, ProjectPack


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
	save_on_top = True
	list_filter = ['name', 'description', 'manager']
	list_display = ['name', 'description', 'manager']
	search_fields = ['name', 'description', 'manager']


@admin.register(ProjectPack)
class ProjectPackAdmin(admin.ModelAdmin):
	save_on_top = True
	list_filter = ['name', 'description', 'status']
	list_display = ['name', 'description', 'status']
	search_fields = ['name', 'description', 'status']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	save_on_top = True
	list_filter = ['name', 'description', 'status']
	list_display = ['name', 'description', 'status']
	search_fields = ['name', 'description', 'status']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	save_on_top = True
	list_filter = ['name', 'description', 'status']
	list_display = ['name', 'description', 'status']
	search_fields = ['name', 'description', 'status']


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
	save_on_top = True
	list_filter = ['file', 'description']
	list_display = ['file', 'description']
	search_fields = ['file', 'description']

@admin.register(SubTaskAttachment)
class SubTaskAttachmentAdmin(admin.ModelAdmin):
	save_on_top = True
	list_filter = ['file', 'description']
	list_display = ['file', 'description']
	search_fields = ['file', 'description']


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
	save_on_top = True
	list_filter = ['name', 'description', 'status']
	list_display = ['name', 'description', 'status']
	search_fields = ['name', 'description', 'status']
