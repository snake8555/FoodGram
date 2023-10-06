from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('recipes/', views.recipes),
    path('recipes/<slug:slug>/', views.recipes_detail),
]
