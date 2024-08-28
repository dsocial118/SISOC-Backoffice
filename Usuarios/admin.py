from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission, Group
from import_export.admin import ImportExportModelAdmin
from .models import *


# region-----------USUARIOS---------------------------------------------------------------------------------------


class UsuariosInline(admin.StackedInline):
    model = Usuarios
    can_delete = False


# Define a new User admin
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    inlines = (UsuariosInline,)


class GroupAdmin(ImportExportModelAdmin):
    pass


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(Permission)
admin.site.register(User, UserAdmin)

# endregion-----------USUARIOS---------------------------------------------------------------------------------------
