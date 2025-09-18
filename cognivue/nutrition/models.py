from django.db import models

class FoodItem(models.Model):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=50, blank=True)
    vitamin_d_iu = models.FloatField(help_text="IU per 100g/serving")
    is_vegetarian = models.BooleanField(default=False)
    is_lactose_free = models.BooleanField(default=False)
    is_nut_free = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class NutritionTip(models.Model):
    title = models.CharField(max_length=200)
    tip_text = models.TextField()
    expanded_text = models.TextField(blank=True)
    related_foods = models.ManyToManyField(FoodItem, blank=True)

    def __str__(self):
        return self.title

class MealPlan(models.Model):
    MEAL_TYPES = [('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner')]
    day = models.CharField(max_length=16)       # e.g., Monday
    meal_type = models.CharField(max_length=16, choices=MEAL_TYPES)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day} - {self.meal_type}: {self.food}"
