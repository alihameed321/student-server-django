from django.urls import path
from .views import api_login, api_logout, api_user_profile, api_refresh_token, api_download_id_card

app_name = 'accounts_api'

urlpatterns = [
    path('login/', api_login, name='api_login'),
    path('logout/', api_logout, name='api_logout'),
    path('profile/', api_user_profile, name='api_user_profile'),
    path('refresh-token/', api_refresh_token, name='api_refresh_token'),
    path('download-id-card/', api_download_id_card, name='api_download_id_card'),
]