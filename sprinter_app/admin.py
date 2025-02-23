from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Sprint, Task

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'created_by', 'created_at')
    filter_horizontal = ('users',)  # Facilita a seleção dos usuários associados

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'sprint', 'status', 'assigned_to', 'created_at', 'updated_at')
    list_filter = ('status', 'sprint')
    search_fields = ('name', 'description')
