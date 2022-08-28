from django.urls import path

from .views import *

app_name = 'equipments'

urlpatterns = [
	path('equipment/list', EquipmentListView.as_view(), name='equipment_list'),
	path('<center_pk>/equipment/list', CenterEquipmentListView.as_view(), name='center_equipment_list'),

	path('equipment/add', EquipmentCreateView.as_view(), name='equipment_create'),
	path('<center_pk>/equipment/add', CenterEquipmentCreateView.as_view(), name='center_equipment_create'),
	path('equipment/<pk>/rent/list', RentListView.as_view(), name='rent_list'),
	path('equipment/type/list', TypeListView.as_view(), name='type_list'),
	path('equipment/<pk>/', EquipmentDetailsView.as_view(), name='equipment_details'),
	path('equipment/<pk>/edit', EquipmentUpdateForm.as_view(), name='equipment_update'),
	path('equipment/delete/<pk>', EquipmentDeleteView.as_view(), name='equipment_delete'),

	path('ajax/', AjaxHandler.as_view(), name='ajax'),
]
