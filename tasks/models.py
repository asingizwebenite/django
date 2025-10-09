from django.db import models

# Create your models here.

class Task(models.Model):
    title = models.CharField(max_length=200)
    description=models.TextField(blank=true)
    created_at = models.DateTimeField(auto_now_add=true)
    completed = models.BooleanField(default=False)


    def __str__(self):
        return sel.title
