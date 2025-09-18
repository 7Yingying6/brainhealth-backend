from django.urls import path
from .views import (
    FoodItemListView,
    NutritionTipListView,
    MealPlanListView,
    swap_meal
)

urlpatterns = [
    path('foods/', FoodItemListView.as_view(), name='nutrition-foods'),
    path('nutrition-tips/', NutritionTipListView.as_view(), name='nutrition-tips'),
    path('meal-plan/', MealPlanListView.as_view(), name='nutrition-meal-plan'),
    path('meal-plan/swap/', swap_meal, name='nutrition-meal-swap'),
]
