from django.urls import path
from . import views

urlpatterns = [
    # Web views
    path('', views.check_points_view, name='check_points'),

    # API endpoints (for Raspberry Pi)
    path('api/deposit/', views.api_deposit, name='api_deposit'),
    path('api/points/<str:register_number>/', views.api_get_points, name='api_get_points'),
]
