from django.contrib import admin
from django.urls import path
from StockApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage),  # Remove the forward slash
]