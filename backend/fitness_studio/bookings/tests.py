from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Instructor, ClassType, FitnessClass, Client, Booking

class BookingAPITestCase(APITestCase):
    
    def setUp(self):
        # Create test data
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            email='instructor@test.com',
            specializations=['Yoga'],
            experience_years=5,
            rating=4.5
        )
        
        self.class_type = ClassType.objects.create(
            name='Test Yoga',
            description='Test yoga class',
            duration_minutes=60,
            difficulty_level='beginner',
            calories_burn_estimate=200
        )
        
        self.fitness_class = FitnessClass.objects.create(
            class_type=self.class_type,
            instructor=self.instructor,
            datetime=timezone.now() + timedelta(days=1),
            max_capacity=20,
            price=1000,
            current_bookings=0
        )
        
        self.client_data = {
            'class_id': str(self.fitness_class.id),
            'client_name': 'Test Client',
            'client_email': 'client@test.com',
            'phone': '+91-9876543210'
        }
    
    def test_get_classes(self):
        """Test GET /api/classes/"""
        url = reverse('class-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('metadata', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_book_class_success(self):
        """Test successful class booking"""
        url = reverse('book-class')
        response = self.client.post(url, self.client_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('booking', response.data)
        
        # Verify booking was created
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.client.email, 'client@test.com')
    
    def test_book_class_duplicate_booking(self):
        """Test duplicate booking prevention"""
        url = reverse('book-class')
        
        # First booking
        response1 = self.client.post(url, self.client_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Duplicate booking
        response2 = self.client.post(url, self.client_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response2.data['success'])
    
    def test_book_class_full_capacity(self):
        """Test booking when class is full"""
        # Fill the class
        self.fitness_class.current_bookings = self.fitness_class.max_capacity
        self.fitness_class.save()
        
        url = reverse('book-class')
        response = self.client.post(url, self.client_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_get_bookings(self):
        """Test GET /api/bookings/"""
        # Create a client and booking
        client = Client.objects.create(
            name='Test Client',
            email='client@test.com'
        )
        
        booking = Booking.objects.create(
            fitness_class=self.fitness_class,
            client=client,
            status='confirmed'
        )
        
        url = reverse('get-bookings')
        response = self.client.get(url, {'email': 'client@test.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['bookings']), 1)
        self.assertIn('client_info', response.data)
        self.assertIn('statistics', response.data)
    
    def test_get_bookings_no_email(self):
        """Test GET /api/bookings/ without email parameter"""
        url = reverse('get-bookings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_cancel_booking(self):
        """Test booking cancellation"""
        # Create a client and booking
        client = Client.objects.create(
            name='Test Client',
            email='client@test.com'
        )
        
        # Create a future class for cancellation
        future_class = FitnessClass.objects.create(
            class_type=self.class_type,
            instructor=self.instructor,
            datetime=timezone.now() + timedelta(days=2),
            max_capacity=20,
            price=1000,
            current_bookings=1
        )
        
        booking = Booking.objects.create(
            fitness_class=future_class,
            client=client,
            status='confirmed'
        )
        
        url = reverse('cancel-booking', args=[booking.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify booking was cancelled
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')

class ModelTestCase(TestCase):
    
    def setUp(self):
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            email='instructor@test.com',
            specializations=['Yoga'],
            experience_years=5
        )
        
        self.class_type = ClassType.objects.create(
            name='Test Yoga',
            description='Test yoga class',
            duration_minutes=60,
            difficulty_level='beginner',
            calories_burn_estimate=200
        )
    
    def test_fitness_class_available_slots(self):
        """Test available_slots property"""
        fitness_class = FitnessClass.objects.create(
            class_type=self.class_type,
            instructor=self.instructor,
            datetime=timezone.now() + timedelta(days=1),
            max_capacity=20,
            current_bookings=5
        )
        
        self.assertEqual(fitness_class.available_slots, 15)
    
    def test_fitness_class_is_bookable(self):
        """Test is_bookable property"""
        # Future class with available slots
        future_class = FitnessClass.objects.create(
            class_type=self.class_type,
            instructor=self.instructor,
            datetime=timezone.now() + timedelta(hours=3),
            max_capacity=20,
            current_bookings=5
        )
        
        self.assertTrue(future_class.is_bookable)
        
        # Past class
        past_class = FitnessClass.objects.create(
            class_type=self.class_type,
            instructor=self.instructor,
            datetime=timezone.now() - timedelta(hours=1),
            max_capacity=20,
            current_bookings=5
        )
        
        self.assertFalse(past_class.is_bookable)
    
    def test_booking_reference_generation(self):
        """Test booking reference auto-generation"""
        client = Client.objects.create(
            name='Test Client',
            email='client@test.com'
        )
        
        fitness_class = FitnessClass.objects.create(
            class_type=self.class_type,
            instructor=self.instructor,
            datetime=timezone.now() + timedelta(days=1),
            max_capacity=20
        )
        
        booking = Booking.objects.create(
            fitness_class=fitness_class,
            client=client
        )
        
        self.assertIsNotNone(booking.booking_reference)
        self.assertTrue(booking.booking_reference.startswith('FB'))