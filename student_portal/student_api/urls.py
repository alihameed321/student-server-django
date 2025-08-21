from django.urls import path
from .views import student_dashboard

app_name = 'student_api'

urlpatterns = [
    path('dashboard/', student_dashboard, name='student_dashboard'),
    # Add more student API endpoints here
]