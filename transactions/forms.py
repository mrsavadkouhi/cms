import datetime

import jdatetime
import openpyxl
from django import forms

from accounts.models import Profile
from centers.models import Center, Project, Task, SubTask, TaskAttachment, STATUS_TYPES, SubTaskAttachment, ProjectPack
from bootstrap_modal_forms.forms import BSModalModelForm

from transactions.models import ProjectPackTransaction, ProjectTransaction, TaskTransaction, Transaction, \
    TransactionAttachment

class TransactionAttachmentForm(BSModalModelForm):
    transaction_id = forms.IntegerField(label='تراکنش', required=True)
    file = forms.FileField(label='پیوست', required=True)
    description = forms.CharField(label='توضیحات', required=False)

    class Meta:
        model = TransactionAttachment
        fields = ['file', 'description']
        # fields = '__all__'
        field_order = ['file', 'description']

    def save(self, commit=True):
        instance = super().save(commit=False)
        transaction = Transaction.objects.get(id=self.cleaned_data['transaction_id'])
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        transaction.attachments.add(instance)
        return self.instance
