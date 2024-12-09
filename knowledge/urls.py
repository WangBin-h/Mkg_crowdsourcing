from django.urls import path
from . import views
from django.urls import path
from .views import register

urlpatterns = [
    path('login/', views.login_in, name='login_in'),
    path('register/', register, name='register'),
]

