
from django.urls import path
from .views import register_view,login_view,home

urlpatterns = [
        path('register/',register_view,name='register-user'),
        path('login/',login_view,name='login-user'),
        path('',home,name='home')
]
