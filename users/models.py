import uuid
from django.db import models

class User(models.Model):
    id = models.UUIDField(
        primary_key=True,    
        default=uuid.uuid4,   
        editable=False    
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=128)
    has_permission_create_user = models.BooleanField(default=False)
    has_permission_create_project = models.BooleanField(default=False)

    def __str__(self):
        return self.email
    
class UserRole(models.Model):
    id = models.UUIDField(
        primary_key=True,    
        default=uuid.uuid4,   
        editable=False    
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.email} - {self.role}"