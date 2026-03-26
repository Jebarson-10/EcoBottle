from decimal import Decimal
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserPoints, Transaction
from .serializers import UserPointsSerializer, DepositSerializer


# ─── Configuration ───────────────────────────────────────────────
POINTS_PER_GRAM = Decimal('0.1')  # 1 point per 10 grams


# ─── API Endpoints (for Raspberry Pi) ───────────────────────────

@api_view(['POST'])
def api_deposit(request):
    """
    Accept a bottle deposit from the Raspberry Pi.
    Expects: { "register_number": "...", "weight_grams": 150.0 }
    Returns: { "points_earned": ..., "total_points": ... }
    """
    serializer = DepositSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    reg_num = serializer.validated_data['register_number']
    weight = Decimal(str(serializer.validated_data['weight_grams']))
    points_earned = weight * POINTS_PER_GRAM

    # Get or create user
    user, created = UserPoints.objects.get_or_create(
        register_number=reg_num,
        defaults={'total_points': Decimal('0')}
    )

    # Create transaction
    Transaction.objects.create(
        user=user,
        weight_grams=weight,
        points_earned=points_earned
    )

    # Update total points
    user.total_points += points_earned
    user.save()

    return Response({
        'register_number': reg_num,
        'points_earned': float(points_earned),
        'total_points': float(user.total_points),
        'message': f'Successfully deposited! Earned {points_earned} points.'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def api_get_points(request, register_number):
    """Get points and transaction history for a register number."""
    try:
        user = UserPoints.objects.get(register_number=register_number)
        serializer = UserPointsSerializer(user)
        return Response(serializer.data)
    except UserPoints.DoesNotExist:
        return Response(
            {'error': 'Register number not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


# ─── Web Views ───────────────────────────────────────────────────

def check_points_view(request):
    """Main page: enter register number to check points."""
    context = {}

    if request.method == 'POST':
        reg_num = request.POST.get('register_number', '').strip()
        if reg_num:
            try:
                user = UserPoints.objects.get(register_number=reg_num)
                transactions = user.transactions.all()[:20]
                context = {
                    'user': user,
                    'transactions': transactions,
                    'found': True,
                    'register_number': reg_num,
                }
            except UserPoints.DoesNotExist:
                context = {
                    'found': False,
                    'register_number': reg_num,
                    'error': f'No records found for register number "{reg_num}".'
                }

    return render(request, 'vending/check_points.html', context)
