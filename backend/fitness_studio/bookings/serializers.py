from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import pytz
from .models import FitnessClass, Booking, Client, Instructor, ClassType

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'specializations', 'experience_years', 'rating']

class ClassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassType
        fields = ['id', 'name', 'description', 'duration_minutes', 'difficulty_level', 
                 'calories_burn_estimate', 'equipment_needed']

class FitnessClassSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    class_type = ClassTypeSerializer(read_only=True)
    available_slots = serializers.ReadOnlyField()
    is_bookable = serializers.ReadOnlyField()
    datetime_local = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessClass
        fields = ['id', 'class_type', 'instructor', 'datetime', 'datetime_local', 
                 'max_capacity', 'current_bookings', 'available_slots', 'price', 
                 'status', 'location', 'special_notes', 'is_bookable']
    
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
        return obj.datetime.isoformat()

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
                else:
                    raise serializers.ValidationError("This class cannot be booked at this time.")
            return value
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Class not found.")
    
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
        fields = ['id', 'name', 'email', 'phone', 'fitness_goals', 'membership_tier', 'total_bookings']

class BookingSerializer(serializers.ModelSerializer):
    fitness_class = FitnessClassSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    can_cancel = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = ['id', 'fitness_class', 'client', 'status', 'booking_datetime', 
                 'booking_reference', 'special_requests', 'payment_status', 
                 'can_cancel', 'feedback_rating', 'feedback_comment']

