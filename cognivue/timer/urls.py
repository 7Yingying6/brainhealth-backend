from django.urls import path
from . import views

urlpatterns = [
    path('', views.timer_page, name='timer_page'),
    path('start/', views.start_timer, name='start_timer'),
    path('timer/<int:minutes>/', views.timer_view, name='timer_with_time'),
    path('timer/', views.timer_view, name='timer'),
    path('api/timer/<int:minutes>/', views.timer_api, name='timer_api'),
    path('api/sessions/', views.save_timer_session, name='save_timer_session'),
    path('api/sessions/list/', views.get_timer_sessions, name='get_timer_sessions'),
]