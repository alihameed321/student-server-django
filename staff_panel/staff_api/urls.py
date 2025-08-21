from django.urls import path
from .views import staff_dashboard

app_name = 'staff_api'

urlpatterns = [
    path('dashboard/', staff_dashboard, name='staff_dashboard'),
    # Add more staff API endpoints here
]