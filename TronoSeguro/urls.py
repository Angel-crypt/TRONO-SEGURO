"""
URL configuration for TronoSeguro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:New Collection
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
from ToiFinder.views import chat_query, LoginView, CatalogView, DetailView, ProfileView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login", LoginView.as_view(), name="login"),
    path("chat/", chat_query, name="chat_query"),
    path('catalog', CatalogView.as_view(), name='catalog'),
    path('catalog/add_bathroom/', CatalogView.as_view(), name='add_bathroom'),
    path('detail/<int:bathroom_id>/', DetailView.as_view(), name='detail'),
    path('profile/', ProfileView.as_view(), name='profile'),
]