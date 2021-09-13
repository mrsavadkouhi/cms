from django.urls import path

from .views import *

app_name = 'transactions'

urlpatterns = [
    path('transaction/list', TransactionListView.as_view(), name='transaction_list'),
    path('<center_pk>/transaction/list', CenterTransactionListView.as_view(), name='center_transaction_list'),

    path('<center_pk>/transaction/<pk>/attach/add', TransactionAttachmentCreateView.as_view(), name='transaction_attach_create'),

    path('transaction/delete/<pk>', TransactionDeleteView.as_view(), name='transaction_delete'),

    path('ajax/', AjaxHandler.as_view(), name='ajax'),
]
