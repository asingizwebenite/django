from  django.urls import path
from . import views

urlpatterns=[
    path('', views.dashboard, name='home'),
    path('login/', views.user_login, name='login')
]