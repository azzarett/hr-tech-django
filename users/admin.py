from django.contrib import admin
from .models import User, UserRole

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'has_permission_create_user', 'has_permission_create_project')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'user')
