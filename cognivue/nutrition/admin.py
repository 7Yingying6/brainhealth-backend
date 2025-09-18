from django.contrib import admin
from .models import FoodItem, NutritionTip, MealPlan

admin.site.register(FoodItem)
admin.site.register(NutritionTip)
admin.site.register(MealPlan)
