from django.contrib import admin
from .models import Project, ProjectStatus, ProjectUser, ProjectTask

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'description')

@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'order', 'project')

@admin.register(ProjectUser)
class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ('project', 'user')

@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'type', 'priority', 'status', 'author', 'assigned_to', 'observer')
    list_filter = ('priority', 'type', 'status')
    search_fields = ('title', 'description')
