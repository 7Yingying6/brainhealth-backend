from django.urls import path
from . import views

urlpatterns = [
    path('', views.vitamin_d_helper, name='vitamin_d_helper'),
    path('update-location/', views.update_location_from_coords, name='update_location_from_coords'),
]