from django.contrib import admin
from .models import Task
class TaskAdmin(admin.ModelAdmin):
    list_display=('title','description','created_at','completed')

# Register your models here.
admin.site.register(Task)