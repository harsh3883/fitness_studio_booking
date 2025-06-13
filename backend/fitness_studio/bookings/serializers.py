from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import pytz
from .models import FitnessClass, Booking, Client, Instructor, ClassType
from django.db.models import Avg

class InstructorSerializer(serializers.ModelSerializer):
    total_classes = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'email', 'specializations', 'bio', 'experience_years', 
                 'rating', 'total_classes', 'is_active']
    
    def get_total_classes(self, obj):
        """Get total number of completed classes for this instructor"""
        return obj.classes.filter(status='completed').count()

class ClassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassType
        fields = ['id', 'name', 'description', 'duration_minutes', 'difficulty_level', 
                 'calories_burn_estimate', 'equipment_needed', 'is_active']

class FitnessClassSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    class_type = ClassTypeSerializer(read_only=True)
    available_slots = serializers.ReadOnlyField()
    is_bookable = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    datetime_local = serializers.SerializerMethodField()
    booking_deadline = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessClass
        fields = ['id', 'class_type', 'instructor', 'datetime', 'datetime_local', 
                 'booking_deadline', 'max_capacity', 'current_bookings', 'available_slots', 
                 'price', 'status', 'location', 'special_notes', 'is_bookable', 'is_past',
                 'created_at', 'updated_at']
    
    def get_datetime_local(self, obj):
        """Convert datetime to user's preferred timezone"""
        request = self.context.get('request')
        if request and hasattr(request, 'user_timezone'):
            user_tz = pytz.timezone(request.user_timezone)
            local_time = obj.datetime.astimezone(user_tz)
            return {
                'datetime': local_time.isoformat(),
                'timezone': str(user_tz),
                'formatted': local_time.strftime('%Y-%m-%d %H:%M %Z')
            }
        return {
            'datetime': obj.datetime.isoformat(),
            'timezone': 'UTC',
            'formatted': obj.datetime.strftime('%Y-%m-%d %H:%M UTC')
        }
    
    def get_booking_deadline(self, obj):
        """Get the booking deadline (2 hours before class)"""
        deadline = obj.datetime - timedelta(hours=2)
        return deadline.isoformat()

class BookingCreateSerializer(serializers.Serializer):
    class_id = serializers.UUIDField()
    client_name = serializers.CharField(max_length=100)
    client_email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    special_requests = serializers.CharField(required=False, allow_blank=True)
    timezone = serializers.CharField(default='Asia/Kolkata')
    
    def validate_class_id(self, value):
        try:
            fitness_class = FitnessClass.objects.get(id=value)
            if not fitness_class.is_bookable:
                if fitness_class.available_slots <= 0:
                    raise serializers.ValidationError("This class is fully booked.")
                elif fitness_class.status != 'scheduled':
                    raise serializers.ValidationError("This class is not available for booking.")
                elif fitness_class.is_past:
                    raise serializers.ValidationError("Cannot book past classes.")
                else:
                    raise serializers.ValidationError("This class cannot be booked at this time.")
            return value
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Class not found.")
    
    def validate_client_email(self, value):
        """Validate email format and check for basic patterns"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Please provide a valid email address.")
        return value.lower()
    
    def validate(self, data):
        # Check if client already has a booking for this class
        try:
            fitness_class = FitnessClass.objects.get(id=data['class_id'])
            client_email = data['client_email']
            
            existing_booking = Booking.objects.filter(
                fitness_class=fitness_class,
                client__email=client_email,
                status__in=['confirmed', 'waitlisted']
            ).exists()
            
            if existing_booking:
                raise serializers.ValidationError("You already have a booking for this class.")
                
        except FitnessClass.DoesNotExist:
            pass
            
        return data

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone', 'emergency_contact', 'medical_conditions',
                 'fitness_goals', 'preferred_timezone', 'membership_tier', 'total_bookings', 
                 'is_active', 'created_at']

class ClientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating client profiles"""
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'emergency_contact', 'medical_conditions',
                 'fitness_goals', 'preferred_timezone']
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True}
        }
    
    def validate_fitness_goals(self, value):
        """Validate fitness goals are provided as a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Fitness goals must be provided as a list.")
        return value

class BookingSerializer(serializers.ModelSerializer):
    fitness_class = FitnessClassSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    can_cancel = serializers.ReadOnlyField()
    time_until_class = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'fitness_class', 'client', 'status', 'booking_datetime', 
                 'booking_reference', 'special_requests', 'payment_status', 
                 'can_cancel', 'feedback_rating', 'feedback_comment', 'reminder_sent',
                 'time_until_class']
    
    def get_time_until_class(self, obj):
        """Get time remaining until the class starts"""
        now = timezone.now()
        time_diff = obj.fitness_class.datetime - now
        
        if time_diff.total_seconds() < 0:
            return "Class has passed"
        
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} days, {hours} hours"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes"

class BookingFeedbackSerializer(serializers.Serializer):
    """Serializer for submitting booking feedback"""
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class InstructorDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for instructor profiles"""
    upcoming_classes = serializers.SerializerMethodField()
    total_completed_classes = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'email', 'specializations', 'bio', 'experience_years', 
                 'rating', 'is_active', 'created_at', 'upcoming_classes', 
                 'total_completed_classes', 'average_rating']
    
    def get_upcoming_classes(self, obj):
        """Get count of upcoming classes for this instructor"""
        return obj.classes.filter(
            datetime__gte=timezone.now(),
            status='scheduled'
        ).count()
    
    def get_total_completed_classes(self, obj):
        """Get total completed classes"""
        return obj.classes.filter(status='completed').count()
    
    def get_average_rating(self, obj):
        """Calculate average rating from completed bookings"""
        avg_rating = Booking.objects.filter(
            fitness_class__instructor=obj,
            status='completed',
            feedback_rating__isnull=False
        ).aggregate(avg_rating=Avg('feedback_rating'))['avg_rating']
        
        return round(avg_rating, 2) if avg_rating else None

class ClassTypeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for class types"""
    upcoming_classes_count = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassType
        fields = ['id', 'name', 'description', 'duration_minutes', 'difficulty_level', 
                 'calories_burn_estimate', 'equipment_needed', 'is_active',
                 'upcoming_classes_count', 'total_bookings']
    
    def get_upcoming_classes_count(self, obj):
        """Get count of upcoming classes for this class type"""
        return obj.classes.filter(
            datetime__gte=timezone.now(),
            status='scheduled'
        ).count()
    
    def get_total_bookings(self, obj):
        """Get total bookings for this class type"""
        return Booking.objects.filter(
            fitness_class__class_type=obj,
            status__in=['confirmed', 'completed']
        ).count()

class BookingStatsSerializer(serializers.Serializer):
    """Serializer for booking statistics"""
    total_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    upcoming_bookings = serializers.IntegerField()
    favorite_class_type = serializers.CharField()
    favorite_instructor = serializers.CharField()
    total_classes_attended = serializers.IntegerField()
    average_rating_given = serializers.FloatField()