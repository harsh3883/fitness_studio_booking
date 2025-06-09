from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
import random
from booking.models import Instructor, ClassType, FitnessClass, Client, Booking

class Command(BaseCommand):
    help = 'Seed the database with sample fitness studio data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Clear existing data
        Booking.objects.all().delete()
        FitnessClass.objects.all().delete()
        Client.objects.all().delete()
        Instructor.objects.all().delete()
        ClassType.objects.all().delete()
        
        # Create Instructors
        instructors_data = [
            {
                'name': 'Priya Sharma',
                'email': 'priya@fitstudio.com',
                'specializations': ['Yoga', 'Meditation', 'Pilates'],
                'bio': 'Certified yoga instructor with 8 years of experience in Hatha and Vinyasa yoga.',
                'experience_years': 8,
                'rating': 4.8
            },
            {
                'name': 'Raj Patel',
                'email': 'raj@fitstudio.com',
                'specializations': ['HIIT', 'CrossFit', 'Strength Training'],
                'bio': 'Former athlete turned fitness trainer specializing in high-intensity workouts.',
                'experience_years': 6,
                'rating': 4.7
            },
            {
                'name': 'Maria Rodriguez',
                'email': 'maria@fitstudio.com',
                'specializations': ['Zumba', 'Dance Fitness', 'Aerobics'],
                'bio': 'Professional dancer and certified Zumba instructor bringing energy to every class.',
                'experience_years': 5,
                'rating': 4.9
            },
            {
                'name': 'David Chen',
                'email': 'david@fitstudio.com',
                'specializations': ['Kickboxing', 'MMA', 'Self Defense'],
                'bio': 'Martial arts expert with black belt in multiple disciplines.',
                'experience_years': 10,
                'rating': 4.6
            }
        ]
        
        instructors = []
        for data in instructors_data:
            instructor = Instructor.objects.create(**data)
            instructors.append(instructor)
            self.stdout.write(f'Created instructor: {instructor.name}')
        
        # Create Class Types
        class_types_data = [
            {
                'name': 'Hatha Yoga',
                'description': 'Gentle yoga focusing on basic postures and breathing techniques. Perfect for beginners.',
                'duration_minutes': 60,
                'difficulty_level': 'beginner',
                'calories_burn_estimate': 150,
                'equipment_needed': ['yoga_mat', 'yoga_blocks', 'strap']
            },
            {
                'name': 'Vinyasa Flow',
                'description': 'Dynamic yoga practice linking breath with movement in flowing sequences.',
                'duration_minutes': 75,
                'difficulty_level': 'intermediate',
                'calories_burn_estimate': 250,
                'equipment_needed': ['yoga_mat', 'towel']
            },
            {
                'name': 'HIIT Cardio',
                'description': 'High-intensity interval training for maximum calorie burn and fitness gains.',
                'duration_minutes': 45,
                'difficulty_level': 'advanced',
                'calories_burn_estimate': 400,
                'equipment_needed': ['dumbbells', 'resistance_bands', 'kettlebells']
            },
            {
                'name': 'Zumba Dance',
                'description': 'Fun, dance-based workout combining Latin rhythms with easy-to-follow moves.',
                'duration_minutes': 60,
                'difficulty_level': 'beginner',
                'calories_burn_estimate': 300,
                'equipment_needed': ['water_bottle', 'towel']
            },
            {
                'name': 'CrossFit WOD',
                'description': 'Constantly varied functional movements performed at high intensity.',
                'duration_minutes': 60,
                'difficulty_level': 'advanced',
                'calories_burn_estimate': 450,
                'equipment_needed': ['barbell', 'dumbbells', 'kettlebells', 'pull_up_bar']
            },
            {
                'name': 'Kickboxing',
                'description': 'High-energy martial arts inspired workout combining punches, kicks, and cardio.',
                'duration_minutes': 50,
                'difficulty_level': 'intermediate',
                'calories_burn_estimate': 350,
                'equipment_needed': ['boxing_gloves', 'hand_wraps', 'punching_bag']
            }
        ]
        
        class_types = []
        for data in class_types_data:
            class_type = ClassType.objects.create(**data)
            class_types.append(class_type)
            self.stdout.write(f'Created class type: {class_type.name}')
        
        # Create Fitness Classes for next 14 days
        now = timezone.now()
        locations = ['Studio 1', 'Studio 2', 'Outdoor Deck', 'Rooftop']
        
        for day_offset in range(14):
            date = now.date() + timedelta(days=day_offset + 1)
            
            # Morning classes (6 AM - 10 AM)
            morning_times = [
                time(6, 0), time(7, 0), time(8, 0), time(9, 0)
            ]
            
            # Evening classes (5 PM - 8 PM)
            evening_times = [
                time(17, 0), time(18, 0), time(19, 0), time(20, 0)
            ]
            
            all_times = morning_times + evening_times
            
            for class_time in all_times:
                # Random class selection
                class_type = random.choice(class_types)
                
                # Select appropriate instructor
                suitable_instructors = [
                    instr for instr in instructors 
                    if any(spec in class_type.name for spec in instr.specializations)
                ]
                
                if not suitable_instructors:
                    instructor = random.choice(instructors)
                else:
                    instructor = random.choice(suitable_instructors)
                
                # Create class
                class_datetime = timezone.make_aware(
                    timezone.datetime.combine(date, class_time)
                )
                
                fitness_class = FitnessClass.objects.create(
                    class_type=class_type,
                    instructor=instructor,
                    datetime=class_datetime,
                    max_capacity=random.randint(15, 25),
                    price=random.randint(500, 1500),  # Price in INR
                    location=random.choice(locations),
                    current_bookings=0
                )
        
        self.stdout.write(f'Created {FitnessClass.objects.count()} fitness classes')
        
        # Create Sample Clients
        clients_data = [
            {
                'name': 'Ananya Gupta',
                'email': 'ananya@email.com',
                'phone': '+91-9876543210',
                'fitness_goals': ['weight_loss', 'flexibility', 'stress_relief'],
                'membership_tier': 'premium'
            },
            {
                'name': 'Rohit Singh',
                'email': 'rohit@email.com',
                'phone': '+91-9876543211',
                'fitness_goals': ['muscle_building', 'strength'],
                'membership_tier': 'basic'
            },
            {
                'name': 'Kavya Menon',
                'email': 'kavya@email.com',
                'phone': '+91-9876543212',
                'fitness_goals': ['cardio', 'endurance', 'weight_loss'],
                'membership_tier': 'premium'
            },
            {
                'name': 'Arjun Nair',
                'email': 'arjun@email.com',
                'phone': '+91-9876543213',
                'fitness_goals': ['martial_arts', 'self_defense'],
                'membership_tier': 'basic'
            }
        ]
        
        clients = []
        for data in clients_data:
            client = Client.objects.create(**data)
            clients.append(client)
            self.stdout.write(f'Created client: {client.name}')
        
        # Create Sample Bookings
        classes = list(FitnessClass.objects.all()[:20])  # First 20 classes
        
        for client in clients:
            # Create random bookings for each client
            client_classes = random.sample(classes, random.randint(2, 5))
            
            for fitness_class in client_classes:
                if fitness_class.available_slots > 0:
                    booking = Booking.objects.create(
                        fitness_class=fitness_class,
                        client=client,
                        status='confirmed',
                        special_requests=random.choice([
                            '', 'First time, please guide', 'Back injury - low impact please',
                            'Prefer front row', 'Need modifications'
                        ])
                    )
                    
                    # Update class booking count
                    fitness_class.current_bookings += 1
                    fitness_class.save()
                    
                    # Update client total bookings
                    client.total_bookings += 1
                    client.save()
        
        self.stdout.write(f'Created {Booking.objects.count()} bookings')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {Instructor.objects.count()} instructors\n'
                f'- {ClassType.objects.count()} class types\n'
                f'- {FitnessClass.objects.count()} fitness classes\n'
                f'- {Client.objects.count()} clients\n'
                f'- {Booking.objects.count()} bookings'
            )
        )