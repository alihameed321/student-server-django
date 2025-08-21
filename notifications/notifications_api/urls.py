from django.urls import path
from .views import user_notifications

app_name = 'notifications_api'

urlpatterns = [
    path('list/', user_notifications, name='user_notifications'),
    # Add more notification API endpoints here
]