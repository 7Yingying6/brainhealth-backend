# models.py
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class SkinType(models.Model):
    SKIN_TYPE_CHOICES = [
        ('I-II', 'Fair Skin Type I-II'),
        ('III-IV', 'Medium Skin Type III-IV'),
        ('V-VI', 'Dark Skin Type V-VI'),
    ]
    
    type = models.CharField(max_length=10, choices=SKIN_TYPE_CHOICES, unique=True)
    min_exposure_minutes = models.IntegerField()
    max_exposure_minutes = models.IntegerField()
    
    def __str__(self):
        return self.get_type_display()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skin_type = models.ForeignKey(SkinType, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, default = "Melbourne")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def has_location(self):
        return self.latitude is not None and self.longitude is not None
    
    def get_location_string(self):
        if self.city:
            return f"{self.city}, AU"
        return 'Melbourne, AU'