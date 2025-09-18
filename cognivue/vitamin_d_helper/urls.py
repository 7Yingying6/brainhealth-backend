from django.urls import path
from . import views

urlpatterns = [
    path('', views.vitamin_d_helper, name='vitamin_d_helper'),
    path('update-location/', views.update_location_from_coords, name='update_location_from_coords'),
    # API endpoints for frontend
    path('api/weather/', views.get_weather_api, name='get_weather_api'),
    path('api/skin-types/', views.get_skin_types_api, name='get_skin_types_api'),
    path('api/recommendation/', views.get_recommendation_api, name='get_recommendation_api'),
]