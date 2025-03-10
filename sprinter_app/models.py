from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User  


class Sprint(models.Model):
    name = models.CharField(max_length=100) 
    description = models.CharField(max_length=500, default="")
    start_date = models.DateField()          
    end_date = models.DateField()           
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sprints")  
    users = models.ManyToManyField(User, related_name="participating_sprints", blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    s3_folder =  models.CharField(max_length=255,default="") 
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'TODO'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name="tasks") 
    name = models.CharField(max_length=200) 
    description = models.TextField(blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO') 
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    storyPoints = models.IntegerField(default=1)

    

    def __str__(self):
        return self.name

