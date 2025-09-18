from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import FoodItem, NutritionTip, MealPlan
from .serializers import FoodItemSerializer, NutritionTipSerializer, MealPlanSerializer

# --- FoodItem list with search + filters ---
class FoodItemListView(generics.ListAPIView):
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        queryset = FoodItem.objects.all()
        q = self.request.query_params.get("q")
        vegetarian = self.request.query_params.get("vegetarian")
        lactose_free = self.request.query_params.get("lactose_free")
        nut_free = self.request.query_params.get("nut_free")

        print(q)

        # Search
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(category__icontains=q))

        # Filters
        if vegetarian == "true":
            queryset = queryset.filter(is_vegetarian=True)
        if lactose_free == "true":
            queryset = queryset.filter(is_lactose_free=True)
        if nut_free == "true":
            queryset = queryset.filter(is_nut_free=True)

        return queryset


# --- Nutrition Tips (already fine, just listing) ---
class NutritionTipListView(generics.ListAPIView):
    queryset = NutritionTip.objects.all()
    serializer_class = NutritionTipSerializer


# --- Meal Plan list ---
class MealPlanListView(generics.ListAPIView):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer


# --- Meal Swap (AC4) ---
@api_view(["POST"])
def swap_meal(request):
    """
    Expects JSON:
    {
        "day": "Monday",
        "meal_type": "lunch",
        "new_food_id": 3
    }
    """
    day = request.data.get("day")
    meal_type = request.data.get("meal_type")
    new_food_id = request.data.get("new_food_id")

    try:
        meal = MealPlan.objects.get(day=day, meal_type=meal_type)
        meal.food_id = new_food_id
        meal.save()
        return Response({"message": "Meal swapped successfully", "meal": MealPlanSerializer(meal).data})
    except MealPlan.DoesNotExist:
        return Response({"error": "Meal not found"}, status=404)
