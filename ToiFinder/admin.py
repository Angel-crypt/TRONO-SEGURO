from django.contrib import admin
from .models import Bathroom, Review, User, Location

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)
@admin.register(Bathroom)
class BathroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'has_accessibility', 'is_free', 'is_clean', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('has_accessibility', 'is_free', 'is_clean')
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('bathroom', 'rating', 'created_at')
    search_fields = ('bathroom__name', 'comment')
    list_filter = ('rating', 'created_at')
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)