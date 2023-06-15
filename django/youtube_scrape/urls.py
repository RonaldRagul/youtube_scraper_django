from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', views.process_csv, name='process_csv'),
    path('get-status/', views.get_status, name='get_status')
]


