from django.urls import path
from . import views

urlpatterns = [
    path('classes/', views.ClassListView.as_view(), name='class-list'),
    path('classes/<uuid:class_id>/', views.get_class_details, name='class-detail'),
    path('book/', views.book_class, name='book-class'),
    path('bookings/', views.get_bookings, name='get-bookings'),
    path('bookings/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
]
