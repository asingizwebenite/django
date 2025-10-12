from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('delete_task/<int:id>/', views.delete_task, name='delete'),
    path('create_task/', views.create_task, name='create'),
    path('update_task/<int:id>/', views.update_task, name='update'),
]