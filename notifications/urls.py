from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notifications Center
    path('', views.NotificationCenterView.as_view(), name='notification_center'),

]