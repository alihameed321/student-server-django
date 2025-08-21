from django.urls import path
from .views import financial_summary

app_name = 'financial_api'

urlpatterns = [
    path('summary/', financial_summary, name='financial_summary'),
    # Add more financial API endpoints here
]