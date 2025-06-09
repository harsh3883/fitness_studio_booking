from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('booking')

def send_booking_confirmation(booking):
    """Send booking confirmation email (mock implementation)"""
    try:
        subject = f"Booking Confirmation - {booking.fitness_class.class_type.name}"
        message = f"""
        Hi {booking.client.name},
        
        Your booking has been confirmed!
        
        Class: {booking.fitness_class.class_type.name}
        Instructor: {booking.fitness_class.instructor.name}
        Date & Time: {booking.fitness_class.datetime.strftime('%Y-%m-%d %H:%M')}
        Location: {booking.fitness_class.location}
        Booking Reference: {booking.booking_reference}
        
        Please arrive 15 minutes early.
        
        Best regards,
        FitStudio Team
        """
        
        # In a real application, you would send actual emails
        logger.info(f"Confirmation email sent to {booking.client.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        return False

def generate_booking_stats(client):
    """Generate booking statistics for a client"""
    from .models import Booking
    
    bookings = client.bookings.all()
    
    return {
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
        'cancelled_bookings': bookings.filter(status='cancelled').count(),
        'upcoming_bookings': bookings.filter(
            status='confirmed',
            fitness_class__datetime__gte=timezone.now()
        ).count(),
        'favorite_class_types': list(
            bookings.values_list('fitness_class__class_type__name', flat=True)
            .distinct()[:3]
        ),
        'member_since': client.created_at.strftime('%Y-%m-%d'),
        'membership_tier': client.membership_tier
    }
