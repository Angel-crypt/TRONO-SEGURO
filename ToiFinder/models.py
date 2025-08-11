# python manage.py makemigrations
# python manage.py migrate
# user = angel
# password = admin123

from django.db import models
from django.utils import timezone

# My models for the ToiFinder app
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['username']

class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ['name']

class Bathroom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='bathrooms')
    has_accessibility = models.BooleanField(default=False)
    is_free = models.BooleanField(default=True)
    is_clean = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Bathroom"
        verbose_name_plural = "Bathrooms"
        ordering = ['name']

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    bathroom = models.ForeignKey(Bathroom, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', default=1)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    
    def __str__(self):
        return f'Review for {self.bathroom.name} - Rating: {self.rating}'
    
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']