from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'is_organizer', 'is_attendee']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_organizer', 'is_attendee')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_organizer', 'is_attendee')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
