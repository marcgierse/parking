"""parking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include

from parking_spaces.views import dashboard_view, booking, freeing, delete_event, signup, release_notes, \
    add_parkingspace, parkingspaces, edit_parkingspace, delete_parkingspace, reclaim, help

urlpatterns = [
    path('admin', admin.site.urls),
    path('', dashboard_view, name="dashboard"),
    path('parking_space', parkingspaces, name="parking_space"),
    path('parking_space/add', add_parkingspace, name="parking_space_add"),
    path('parking_space/<int:parking_space>/edit', edit_parkingspace, name="parking_space_edit"),
    path('parking_space/<int:parking_space>/delete', delete_parkingspace, name="parking_space_delete"),
    path('parking_space/<int:parking_space>/<str:date>/free', freeing, name="free"),
    path('parking_space/<int:parking_space>/<str:date>/book', booking, name="book"),
    path('parking_space/<int:parking_space>/<str:date>/reclaim', reclaim, name="reclaim"),
    path('parking_space_event/<int:event_id>/delete', delete_event, name="delete"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup', signup, name="signup"),
    path('hilfe', help, name="help"),
    path('release_notes', release_notes, name="release_notes"),
]
