from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path("brain-health-news/", views.curated_news_list, name="brain_health_news"),
]
