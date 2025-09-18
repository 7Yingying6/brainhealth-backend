from django.contrib import admin
from .models import Factoid, LifestyleTip

@admin.register(Factoid)
class FactoidAdmin(admin.ModelAdmin):
    list_display = ("title", "badge", "source_name", "order_index", "is_active")
    list_editable = ("order_index", "is_active")
    search_fields = ("title", "text", "source_name")

@admin.register(LifestyleTip)
class LifestyleTipAdmin(admin.ModelAdmin):
    list_display = ("title", "impact", "order_index", "is_active")
    list_editable = ("impact", "order_index", "is_active")
    search_fields = ("title", "front_summary", "back_detail")
