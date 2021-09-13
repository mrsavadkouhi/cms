from django.contrib import admin

from .models import Equipment, Rent


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['name', 'description', 'owner']
    list_display = ['name', 'description', 'owner']
    search_fields = ['name', 'description', 'owner']


@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['borrower', 'center', 'project', 'is_reservation']
    list_display = ['borrower', 'center', 'project', 'is_reservation']
    search_fields = ['borrower', 'center', 'project', 'is_reservation']
