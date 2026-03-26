from rest_framework import serializers
from .models import UserPoints, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'weight_grams', 'points_earned', 'timestamp']


class UserPointsSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = UserPoints
        fields = ['register_number', 'total_points', 'created_at', 'updated_at', 'transactions']


class DepositSerializer(serializers.Serializer):
    register_number = serializers.CharField(max_length=50)
    weight_grams = serializers.DecimalField(max_digits=8, decimal_places=2)
