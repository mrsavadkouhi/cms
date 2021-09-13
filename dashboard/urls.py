from django.urls import path

from .views import *

app_name = 'dashboard'

urlpatterns = [
	path('login/', CustomLoginView.as_view(), name='login'),

	# Dashboard
	path('', MyTasks.as_view(), name='main'),
	path('task/<pk>/attach/add', TaskAttachmentCreateView.as_view(), name='mytask_attach_create'),
	path('subtask/<pk>/attach/add', SubTaskAttachmentCreateView.as_view(), name='mysubtask_attach_create'),
	path('myprojectpacks', MyProjectPacks.as_view(), name='myprojectpacks'),
	path('mycenter', MyCeneter.as_view(), name='mycenter'),
]
