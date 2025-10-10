from  django.urls import path
from . import views

urlpatterns=[
    path('', views.dashboard, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('dashboard/',views.dashboard, name='dashboard')
]