from django.contrib import admin
from .models import CuratedArticle

@admin.register(CuratedArticle)
class CuratedArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "author", "date_published")
    list_filter = ("source",)
    search_fields = ("title", "author", "source", "url")

