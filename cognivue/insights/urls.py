from django.urls import path
from . import views

app_name = "insights"

urlpatterns = [
    # API endpoints for Vue frontend
    path("api/dashboard/", views.dashboard, name="api_dashboard"),
    path("api/questionnaire/start/", views.questionnaire_start, name="api_questionnaire_start"),
    path("api/questionnaire/question/<int:index>/", views.questionnaire_question, name="api_question"),
    path("api/questionnaire/result/", views.questionnaire_result, name="api_questionnaire_result"),
    path("api/disclaimer/", views.disclaimer, name="api_disclaimer"),
    path("api/learn-more/", views.learn_more, name="api_learn_more"),
    path("api/factoids/", views.api_factoids, name="api_factoids"),
    path("api/tips/", views.api_tips, name="api_tips"),
]
