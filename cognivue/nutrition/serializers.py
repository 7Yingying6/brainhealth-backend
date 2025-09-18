from rest_framework import serializers
from .models import FoodItem, NutritionTip, MealPlan

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = "__all__"

class NutritionTipSerializer(serializers.ModelSerializer):
    related_foods = FoodItemSerializer(many=True, read_only=True)
    class Meta:
        model = NutritionTip
        fields = "__all__"

class MealPlanSerializer(serializers.ModelSerializer):
    food = FoodItemSerializer(read_only=True)
    class Meta:
        model = MealPlan
        fields = "__all__"
