from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils import timezone
from datetime import timedelta
import uuid

class Instructor(models.Model):
    """Model for fitness instructors"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    specializations = models.JSONField(default=list, help_text="List of specializations")
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00,
                               validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({', '.join(self.specializations)})"
    
    class Meta:
        ordering = ['name']

class ClassType(models.Model):
    """Model for different types of fitness classes"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    calories_burn_estimate = models.PositiveIntegerField(help_text="Estimated calories burned")
    equipment_needed = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.difficulty_level})"
    
    class Meta:
        ordering = ['name']

class FitnessClass(models.Model):
    """Model for individual fitness class sessions"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, related_name='classes')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='classes')
    datetime = models.DateTimeField()
    max_capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])
    current_bookings = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    location = models.CharField(max_length=100, default="Studio 1")
    special_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def available_slots(self):
        return max(0, self.max_capacity - self.current_bookings)
    
    @property
    def is_bookable(self):
        now = timezone.now()
        min_booking_time = now + timedelta(hours=2)
        return (
            self.status == 'scheduled' and
            self.datetime > min_booking_time and
            self.available_slots > 0
        )
    
    @property
    def is_past(self):
        return self.datetime < timezone.now()
    
    def __str__(self):
        return f"{self.class_type.name} - {self.datetime.strftime('%Y-%m-%d %H:%M')} with {self.instructor.name}"
    
    class Meta:
        ordering = ['datetime']
        unique_together = ['instructor', 'datetime']

class Client(models.Model):
    """Model for clients/users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_conditions = models.TextField(blank=True)
    fitness_goals = models.JSONField(default=list)
    preferred_timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    is_active = models.BooleanField(default=True)
    total_bookings = models.PositiveIntegerField(default=0)
    membership_tier = models.CharField(max_length=20, default='basic')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    class Meta:
        ordering = ['name']

class Booking(models.Model):
    """Model for class bookings"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('waitlisted', 'Waitlisted'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    booking_datetime = models.DateTimeField(auto_now_add=True)
    special_requests = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    booking_reference = models.CharField(max_length=20, unique=True)
    reminder_sent = models.BooleanField(default=False)
    feedback_rating = models.PositiveIntegerField(null=True, blank=True,
                                                validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback_comment = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"FB{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def can_cancel(self):
        now = timezone.now()
        cancellation_deadline = self.fitness_class.datetime - timedelta(hours=4)
        return now < cancellation_deadline and self.status == 'confirmed'
    
    def __str__(self):
        return f"{self.client.name} - {self.fitness_class} ({self.status})"
    
    class Meta:
        ordering = ['-booking_datetime']
        unique_together = ['fitness_class', 'client']