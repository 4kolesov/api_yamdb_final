from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'date_joined',
        'role',
        'email',
        'first_name',
        'last_name',
        'is_active'
    )
    search_fields = ('username', 'email')
    list_filter = ('date_joined',)
    list_editable = ('role', 'is_active',)


admin.site.register(User, UserAdmin)
