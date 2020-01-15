"""Invoice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users import views as usersviews
from home import views as homeviews

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', usersviews.login),
    path('/',usersviews.login),
    path('login/', usersviews.login, name='login'),
    path('logout/', usersviews.logout, name='logout'),
    path('register/', usersviews.register, name='register'),
    path('dashboard/', homeviews.dashboard, name='dashboard'),
    path('adminhome/', homeviews.adminhome, name='adminhome'),
    path('invoices/',homeviews.invoices,name='invoices'),
]
