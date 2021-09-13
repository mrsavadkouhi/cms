from django.urls import path

from .views import *

app_name = 'accounts'

urlpatterns = [
	# Security
	path('check-file-access-permission/<path:request_path_uri>', MediaFileAccessController.as_view(), name='media_access_control'),

	path('profile/list', ProfileListView.as_view(), name='profile_list'),
	path('<center_pk>/profiles', CenterProfileListView.as_view(), name='center_profile_list'),
	path('<project_pk>/profiles', ProjectProfileListView.as_view(), name='project_profile_list'),
	# path('profile/superusers/api', APISuperuserListView.as_view(), name='superuser_list_api'),

	# path('centermanagers', CentermanagerListView.as_view(), name='centermanager_list'),
	# path('profile/centermanagers/api', APICentermanagerListView.as_view(), name='centermanager_list_api'),

	# path('projectmanagers', ProjectmanagerListView.as_view(), name='projectmanager_list'),
	# path('profile/projectmanagers/api', APIProjectmanagerListView.as_view(), name='projectmanager_list_api'),

	# path('employees', EmployeeListView.as_view(), name='employees_list'),
	# path('profile/employees/api', APIEmployeeListView.as_view(), name='employees_list_api'),

	path('profile/add', ProfileCreateView.as_view(), name='profile_create'),
	path('<center_pk>/profile/add', CenterProfileCreateView.as_view(), name='center_profile_create'),
	# path('profile/add_json', JsonProfileCreateView.as_view(), name='who_create_json'),
	path('profile/<pk>/', ProfileDetailsView.as_view(), name='profile_details'),
	path('profile/<pk>/edit', ProfileUpdateForm.as_view(), name='profile_update'),
	path('<center_pk>/profile/<pk>/edit', CenterProfileUpdateForm.as_view(), name='center_profile_update'),
	path('profile/delete/<pk>', ProfileDeleteView.as_view(), name='profile_delete'),
]
