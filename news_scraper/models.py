from django.db import models

class Article(models.Model):
    url = models.URLField(max_length=500, unique=True)
    title = models.CharField(max_length=300, blank=True)
    source_domain = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    keywords_found = models.CharField(max_length=200, blank=True)
    date_published = models.DateTimeField(null=True, blank=True)
    date_collected = models.DateTimeField(auto_now_add=True)
    has_keywords = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.source_domain} - {self.title or 'No Title'}"

    class Meta:
        ordering = ['-date_collected']

class CuratedArticle(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120, blank=True)
    image_url = models.URLField(blank=True)
    url = models.URLField(help_text="External article URL")
    source = models.CharField(max_length=120, help_text="Publisher (e.g., UniSA, ABS, SBS)")
    date_published = models.DateTimeField()

    class Meta:
        ordering = ["-date_published"]  # latest first

    def __str__(self):
        return self.title
