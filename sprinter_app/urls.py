from django.urls import path
from . import views  
from django.urls import path, include
from .views import finish_sprint
urlpatterns = [
    path('', views.mainPage, name='mainPage'),
    path('accounts/', include('allauth.urls')),
    path('create-sprint/', views.create_sprint, name='create_sprint'),
    path('create_task/<int:sprint_id>/', views.create_task, name='create_task'),
    path('update_task_state/', views.update_task_state, name='update_task_state'),
    path('sprint/<int:sprint_id>/add_guest/', views.add_guest, name='add_guest'),
    path('finish_sprint/<int:sprint_id>/', finish_sprint, name='finish_sprint'),
]
