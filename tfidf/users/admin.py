from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User


class MyUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if request.user.is_superuser:
            # perm_fields = ('is_active', 'is_staff', 'is_superuser',
            #                'groups', 'user_permissions')
            perm_fields = (
                'is_active', 'is_staff', 'user_permissions', 'groups'
            )
        else:
            # modify these to suit the fields you want your
            # staff user to be able to edit
            # perm_fields = ('is_active', 'is_staff')
            perm_fields = ()

        return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': perm_fields}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')})]


admin.site.register(User, MyUserAdmin)
