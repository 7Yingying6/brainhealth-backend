from django.db import models

class Factoid(models.Model):
    """Slide for the rotating jumbotron."""
    title = models.CharField(max_length=120)             # e.g., "Dementia Protection"
    text = models.TextField()                             # slide body
    badge = models.CharField(max_length=32, blank=True, default="")  # e.g., "Fact 1 of 6"
    source_name = models.CharField(max_length=120, blank=True, default="")
    source_url = models.URLField(blank=True, default="")
    icon = models.CharField(max_length=64, blank=True, default="")   # optional icon key/emoji
    order_index = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order_index", "id"]

    def __str__(self):
        return self.title


class LifestyleTip(models.Model):
    """Content for the flippable lifestyle cards."""
    IMPACT = (("beneficial", "Beneficial"), ("concerning", "Concerning"))

    title = models.CharField(max_length=120)                         # "Daily Sun Exposure"
    impact = models.CharField(max_length=16, choices=IMPACT)         # chip colour
    front_summary = models.CharField(max_length=140)                 # short teaser
    back_detail = models.TextField()                                 # detailed explanation
    icon = models.CharField(max_length=64, blank=True, default="")   # optional
    order_index = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order_index", "id"]

    def __str__(self):
        return self.title
