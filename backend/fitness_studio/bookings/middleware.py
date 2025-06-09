import pytz
from django.utils.deprecation import MiddlewareMixin

class TimezoneMiddleware(MiddlewareMixin):
    """Middleware to handle timezone for each request"""
    
    def process_request(self, request):
        timezone_header = request.META.get('HTTP_X_TIMEZONE', 'Asia/Kolkata')
        
        # Validate timezone
        try:
            pytz.timezone(timezone_header)
            request.user_timezone = timezone_header
        except pytz.exceptions.UnknownTimeZoneError:
            request.user_timezone = 'Asia/Kolkata' 