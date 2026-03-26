"""
Script to populate the database with sample data for testing.
Run: python manage.py shell < create_test_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bottle_vending.settings')
django.setup()

from decimal import Decimal
from vending.models import UserPoints, Transaction

# Sample users with register numbers
test_data = [
    {
        'register_number': 'REG001',
        'deposits': [
            {'weight': 150, 'points': 15.0},
            {'weight': 200, 'points': 20.0},
            {'weight': 100, 'points': 10.0},
        ]
    },
    {
        'register_number': 'REG002',
        'deposits': [
            {'weight': 300, 'points': 30.0},
            {'weight': 250, 'points': 25.0},
        ]
    },
    {
        'register_number': '2024CS101',
        'deposits': [
            {'weight': 180, 'points': 18.0},
            {'weight': 220, 'points': 22.0},
            {'weight': 350, 'points': 35.0},
            {'weight': 120, 'points': 12.0},
        ]
    },
]

for data in test_data:
    user, created = UserPoints.objects.get_or_create(
        register_number=data['register_number'],
        defaults={'total_points': Decimal('0')}
    )

    if created:
        total = Decimal('0')
        for deposit in data['deposits']:
            Transaction.objects.create(
                user=user,
                weight_grams=Decimal(str(deposit['weight'])),
                points_earned=Decimal(str(deposit['points']))
            )
            total += Decimal(str(deposit['points']))

        user.total_points = total
        user.save()
        print(f"Created user {data['register_number']} with {total} points")
    else:
        print(f"User {data['register_number']} already exists")

print("\nDone! Test data created successfully.")
