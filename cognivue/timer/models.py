from django.db import models
from django.contrib.auth.models import User

class TimerSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in seconds")  # Store in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    def formatted_duration(self):
        """Convert seconds to MM:SS format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def __str__(self):
        return f"{self.formatted_duration()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"