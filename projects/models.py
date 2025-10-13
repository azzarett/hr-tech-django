import uuid
from django.db import models

from users.models import User

class Project(models.Model):
    id = models.UUIDField(
        primary_key=True,    
        default=uuid.uuid4,   
        editable=False    
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    key = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name
    
class ProjectStatus(models.Model):
    id = models.UUIDField(
        primary_key=True,    
        default=uuid.uuid4,   
        editable=False    
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.project.name} - {self.status}"
    
class ProjectUser(models.Model):
    id = models.UUIDField(
        primary_key=True,    
        default=uuid.uuid4,   
        editable=False    
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.project.name} - {self.user.email}"
    
class ProjectTask(models.Model):
    id = models.UUIDField(
        primary_key=True,    
        default=uuid.uuid4,   
        editable=False    
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authored_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    observer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='observed_tasks')
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField()
    type = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
