from django.contrib import admin

from .models import Profile, Lang, Software, Permission


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'get_first_name', 'get_last_name']
    search_fields = ['user__username', 'user__first_name', ]
    save_as = True
    save_on_top = True

    def get_username(self, obj):
        return obj.user.username

    get_username.admin_order_field = 'Username'  # Allows column order sorting
    get_username.short_description = "Username"  # Renames column head

    def get_first_name(self, obj):
        return obj.user.first_name

    get_first_name.admin_order_field = 'First name'  # Allows column order sorting
    get_first_name.short_description = "First Name"  # Renames column head

    def get_last_name(self, obj):
        return obj.user.last_name

    get_last_name.admin_order_field = 'Last name'  # Allows column order sorting
    get_last_name.short_description = "Last name"  # Renames column head


@admin.register(Lang)
class LangAdmin(admin.ModelAdmin):
    list_display = ['name',]
    search_fields = ['name',]
    save_as = True
    save_on_top = True


@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ['name',]
    search_fields = ['name',]
    save_as = True
    save_on_top = True

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['code',]
    search_fields = ['code',]
    save_as = True
    save_on_top = True
