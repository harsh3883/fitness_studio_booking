from django.urls import path, include
from . import views

urlpatterns = [
    # Existing booking endpoints
    path('classes/', views.ClassListView.as_view(), name='class-list'),
    path('classes/<uuid:class_id>/', views.get_class_details, name='class-detail'),
    path('book/', views.book_class, name='book-class'),
    path('bookings/', views.get_bookings, name='get-bookings'),
    path('bookings/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    
    # Authentication endpoints (add these)
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/profile/', views.get_user_profile, name='profile'),
    
    # Alternative: Use Django REST Framework's built-in auth
    # path('auth/', include('rest_framework.urls')),
]