from django.urls import path
from . import views

app_name = 'staff_panel'

urlpatterns = [
    # Main Dashboard
    path('', views.StaffDashboardView.as_view(), name='dashboard'),
    

]