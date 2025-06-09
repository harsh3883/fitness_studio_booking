from django.contrib import admin
from .models import Instructor, ClassType, FitnessClass, Client, Booking

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name', 'experience_years', 'rating', 'is_active']
    list_filter = ['is_active', 'experience_years']
    search_fields = ['name', 'email']

@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty_level', 'duration_minutes', 'is_active']
    list_filter = ['difficulty_level', 'is_active']

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ['class_type', 'instructor', 'datetime', 'available_slots', 'status']
    list_filter = ['status', 'class_type', 'instructor']
    search_fields = ['class_type__name', 'instructor__name']
    date_hierarchy = 'datetime'

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'total_bookings', 'membership_tier', 'is_active']
    list_filter = ['membership_tier', 'is_active']
    search_fields = ['name', 'email']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'client', 'fitness_class', 'status', 'booking_datetime']
    list_filter = ['status', 'fitness_class__class_type']
    search_fields = ['booking_reference', 'client__name', 'client__email']
    date_hierarchy = 'booking_datetime'
