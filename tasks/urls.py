from  django.urls import path
from . import views

urlpatterns=[
    path('', views.landing, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('update/<int:id>/',views.update_task, name='update'),
    path('create/',views.create_task, name='create'),
    path('delete/<int:id>/', views.delete_task, name='delete'),
    path('tasks/',views.tasks, name='tasks'),
    path('logout/', views.user_logout, name='logout')

]