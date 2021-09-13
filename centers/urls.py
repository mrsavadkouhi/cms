from django.urls import path

from .views import *

app_name = 'centers'

urlpatterns = [
	path('center/list', CenterListView.as_view(), name='center_list'),
	path('center/add', CenterCreateView.as_view(), name='center_create'),
	path('center/<pk>/', CenterDetailsView.as_view(), name='center_details'),
	path('center/<pk>/edit', CenterUpdateForm.as_view(), name='center_update'),
	path('center/delete/<pk>', CenterDeleteView.as_view(), name='center_delete'),

	path('projectpack/list', ProjectPackListView.as_view(), name='projectpack_list'),
	path('<center_pk>/projectpack/list', CenterProjectPackListView.as_view(), name='center_projectpack_list'),

	path('projectpack/add', ProjectPackCreateView.as_view(), name='projectpack_create'),
	path('<center_pk>/projectpack/add', CenterProjectPackCreateView.as_view(), name='center_projectpack_create'),

	path('projectpack/<pk>/attach/add', ProjectPackAttachmentCreateView.as_view(),name='projectpack_attach_create'),
	path('project/attach/delete/<pk>', ProjectPackAttachmentDeleteView.as_view(), name='projectpack_attach_delete'),
	path('projectpack/<pk>/', ProjectPackDetailsView.as_view(), name='projectpack_details'),
	path('projectpack/<pk>/edit', ProjectPackUpdateView.as_view(), name='projectpack_update'),
	path('<center_pk>/projectpack/<pk>/edit', CenterProjectPackUpdateView.as_view(), name='center_projectpack_update'),
	path('projectpack/delete/<pk>', ProjectPackDeleteView.as_view(), name='projectpack_delete'),

	path('<projectpack_pk>/project/lilst', ProjectPackProjectListView.as_view(), name='projectpack_project_list'),
	path('<projectpack_pk>/project/add', ProjectPackProjectCreateView.as_view(), name='projectpack_project_create'),
	path('<projectpack_pk>/project/<pk>/attach/add', ProjectAttachmentCreateView.as_view(), name='project_attach_create'),
	path('project/attach/delete/<pk>', ProjectAttachmentDeleteView.as_view(), name='project_attach_delete'),
	path('<projectpack_pk>/project/<pk>/', ProjectPackProjectDetailsView.as_view(), name='projectpack_project_details'),
	path('<projectpack_pk>/project/<pk>/edit', ProjectPackProjectUpdateForm.as_view(), name='projectpack_project_update'),
	path('project/delete/<pk>', ProjectPackProjectDeleteView.as_view(), name='projectpackـproject_delete'),

	path('<pk_project>/task/list', TaskListView.as_view(), name='task_list'),
	path('task/update/<pk>', TaskUpdateView.as_view(), name='task_update'),
	path('task/<pk>/attach/add', TaskAttachmentCreateView.as_view(), name='task_attach_create'),
	path('subtask/<pk>/attach/add', SubTaskAttachmentCreateView.as_view(), name='subtask_attach_create'),
	path('subtask/update/<pk>', SubTaskUpdateView.as_view(), name='subtask_update'),
	path('task/delete/<pk>', TaskDeleteView.as_view(), name='task_delete'),
	path('subtask/delete/<pk>', SubTaskDeleteView.as_view(), name='subtask_delete'),

	path('project/bulk_add', ProjectBulkCreateView.as_view(), name='project_bulk_create'),
	path('task/bulk_add', TaskBulkCreateView.as_view(), name='task_bulk_create'),

	path('ajax/', AjaxHandler.as_view(), name='ajax'),
]
