from rest_framework import generics, status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from datetime import timedelta
import logging
from .models import FitnessClass, Booking, Client, Instructor, ClassType
from .serializers import (
    FitnessClassSerializer, BookingCreateSerializer, 
    BookingSerializer, ClientSerializer
)
from .utils import send_booking_confirmation, generate_booking_stats

logger = logging.getLogger('booking')

class ClassListView(generics.ListAPIView):
    """
    GET /api/classes
    Returns upcoming fitness classes with filtering and search
    """
    serializer_class = FitnessClassSerializer
    
    def get_queryset(self):
        queryset = FitnessClass.objects.filter(
            datetime__gte=timezone.now(),
            status='scheduled'
        ).select_related('instructor', 'class_type')
        
        # Filtering
        class_type = self.request.query_params.get('type')
        instructor = self.request.query_params.get('instructor')
        date = self.request.query_params.get('date')
        difficulty = self.request.query_params.get('difficulty')
        available_only = self.request.query_params.get('available_only', 'false').lower() == 'true'
        
        if class_type:
            queryset = queryset.filter(class_type__name__icontains=class_type)
        
        if instructor:
            queryset = queryset.filter(instructor__name__icontains=instructor)
            
        if date:
            queryset = queryset.filter(datetime__date=date)
            
        if difficulty:
            queryset = queryset.filter(class_type__difficulty_level=difficulty)
            
        if available_only:
            queryset = queryset.filter(current_bookings__lt=models.F('max_capacity'))
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        # Add caching for better performance
        cache_key = f"classes_list_{hash(str(request.GET))}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            return Response(cached_response)
        
        response = super().list(request, *args, **kwargs)
        
        # Add metadata
        response.data['metadata'] = {
            'total_classes': self.get_queryset().count(),
            'available_slots': sum(cls.available_slots for cls in self.get_queryset()),
            'upcoming_days': 7,
            'filters_applied': bool(request.query_params)
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, response.data, 300)
        
        logger.info(f"Classes listed: {len(response.data.get('results', []))} classes returned")
        return response

@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def book_class(request):
    """
    POST /api/book
    Create a new booking for a fitness class
    """
    serializer = BookingCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.warning(f"Invalid booking request: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Invalid booking data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Get or create client
            client_data = {
                'name': serializer.validated_data['client_name'],
                'email': serializer.validated_data['client_email'],
            }
            
            if serializer.validated_data.get('phone'):
                client_data['phone'] = serializer.validated_data['phone']
            
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            
            # Get fitness class
            fitness_class = get_object_or_404(FitnessClass, id=serializer.validated_data['class_id'])
            
            # Double-check availability (race condition protection)
            if not fitness_class.is_bookable:
                return Response({
                    'success': False,
                    'message': 'Class is no longer available for booking'
                }, status=status.HTTP_409_CONFLICT)
            
            # Create booking
            booking = Booking.objects.create(
                fitness_class=fitness_class,
                client=client,
                special_requests=serializer.validated_data.get('special_requests', ''),
                status='confirmed'
            )
            
            # Update class booking count
            fitness_class.current_bookings += 1
            fitness_class.save()
            
            # Update client total bookings
            client.total_bookings += 1
            client.save()
            
            # Send confirmation (in real app, this would be async)
            try:
                send_booking_confirmation(booking)
            except Exception as e:
                logger.error(f"Failed to send confirmation email: {e}")
            
            logger.info(f"New booking created: {booking.booking_reference} for {client.email}")
            
            return Response({
                'success': True,
                'message': 'Booking confirmed successfully!',
                'booking': {
                    'id': str(booking.id),
                    'reference': booking.booking_reference,
                    'class_name': fitness_class.class_type.name,
                    'instructor': fitness_class.instructor.name,
                    'datetime': fitness_class.datetime.isoformat(),
                    'location': fitness_class.location,
                    'status': booking.status
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Booking creation failed: {e}")
        return Response({
            'success': False,
            'message': 'An error occurred while processing your booking'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_bookings(request):
    """
    GET /api/bookings?email=user@example.com
    Returns all bookings for a specific email address
    """
    email = request.query_params.get('email')
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        client = get_object_or_404(Client, email=email)
        bookings = Booking.objects.filter(client=client).select_related(
            'fitness_class__instructor', 
            'fitness_class__class_type'
        )
        
        # Filter by status if requested
        status_filter = request.query_params.get('status')
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        serializer = BookingSerializer(bookings, many=True, context={'request': request})
        
        # Add summary statistics
        stats = generate_booking_stats(client)
        
        logger.info(f"Bookings retrieved for {email}: {bookings.count()} bookings")
        
        return Response({
            'success': True,
            'bookings': serializer.data,
            'client_info': ClientSerializer(client).data,
            'statistics': stats
        })
        
    except Client.DoesNotExist:
        logger.warning(f"Booking lookup for non-existent client: {email}")
        return Response({
            'success': False,
            'message': 'No bookings found for this email address',
            'bookings': [],
            'client_info': None,
            'statistics': {}
        })

@api_view(['POST'])
def cancel_booking(request, booking_id):
    """
    POST /api/bookings/{booking_id}/cancel
    Cancel a specific booking
    """
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        if not booking.can_cancel:
            return Response({
                'success': False,
                'message': 'This booking cannot be cancelled. Cancellation deadline has passed.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            booking.status = 'cancelled'
            booking.save()
            
            # Update class booking count
            fitness_class = booking.fitness_class
            fitness_class.current_bookings = max(0, fitness_class.current_bookings - 1)
            fitness_class.save()
        
        logger.info(f"Booking cancelled: {booking.booking_reference}")
        
        return Response({
            'success': True,
            'message': 'Booking cancelled successfully'
        })
        
    except Exception as e:
        logger.error(f"Booking cancellation failed: {e}")
        return Response({
            'success': False,
            'message': 'An error occurred while cancelling the booking'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_class_details(request, class_id):
    """
    GET /api/classes/{class_id}
    Get detailed information about a specific class
    """
    try:
        fitness_class = get_object_or_404(
            FitnessClass.objects.select_related('instructor', 'class_type'),
            id=class_id
        )
        
        serializer = FitnessClassSerializer(fitness_class, context={'request': request})
        
        # Add additional details
        bookings_count = fitness_class.bookings.filter(status='confirmed').count()
        recent_bookings = fitness_class.bookings.filter(
            status='confirmed'
        ).select_related('client')[:5]
        
        return Response({
            'success': True,
            'class': serializer.data,
            'booking_details': {
                'confirmed_bookings': bookings_count,
                'waitlist_count': fitness_class.bookings.filter(status='waitlisted').count(),
                'recent_bookings': [
                    {'client_name': booking.client.name, 'booking_time': booking.booking_datetime}
                    for booking in recent_bookings
                ]
            }
        })
        
    except FitnessClass.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Class not found'
        }, status=status.HTTP_404_NOT_FOUND)
