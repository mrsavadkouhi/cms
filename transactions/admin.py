from django.contrib import admin

from transactions.models import ProjectPackTransaction, ProjectTransaction, TaskTransaction


@admin.register(ProjectPackTransaction)
class ProjectPackTransactionAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['tittle', 'project_pack', 'value']
    list_display = ['tittle', 'project_pack', 'value']
    search_fields = ['tittle', 'project_pack', 'value']


@admin.register(ProjectTransaction)
class ProjectTransactionAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['tittle', 'project', 'value']
    list_display = ['tittle', 'project', 'value']
    search_fields = ['tittle', 'project', 'value']

@admin.register(TaskTransaction)
class TaskTransactionAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['tittle', 'task', 'value']
    list_display = ['tittle', 'task', 'value']
    search_fields = ['tittle', 'task', 'value']
