import datetime

import jdatetime
import openpyxl
from django import forms

from centers.models import Center
from .models import Equipment, EQUIPMENT_TYPES, EquipmentType


class EquipmentForm(forms.ModelForm):
    owner = forms.ModelChoiceField(queryset=Center.objects.all())
    type = forms.ModelChoiceField(queryset=EquipmentType.objects.all())
    # type = forms.ChoiceField(choices=EQUIPMENT_TYPES)

    class Meta:
        model = Equipment
        fields = '__all__'
        field_order = ['name', 'description', 'owner', 'type']