from django.urls import path
from . import views  
from django.urls import path, include
from .views import finish_sprint
from .views import get_sprint_files
from .views import upload_sprint_file
urlpatterns = [
    path('', views.mainPage, name='mainPage'),
    path('accounts/', include('allauth.urls')),
    path('create-sprint/', views.create_sprint, name='create_sprint'),
    path('create_task/<int:sprint_id>/', views.create_task, name='create_task'),
    path('update_task_state/', views.update_task_state, name='update_task_state'),
    path('sprint/<int:sprint_id>/add_guest/', views.add_guest, name='add_guest'),
    path('finish_sprint/<int:sprint_id>/', finish_sprint, name='finish_sprint'),
    path("sprint/<int:sprint_id>/files/", get_sprint_files, name="get_sprint_files"),
    path("sprint/<int:sprint_id>/upload/", upload_sprint_file, name="upload_sprint_file"),
    path('remove_file/', views.remove_file, name='remove_file'),
]
