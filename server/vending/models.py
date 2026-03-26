from django.db import models


class UserPoints(models.Model):
    register_number = models.CharField(max_length=50, unique=True, db_index=True)
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Points"
        verbose_name_plural = "User Points"
        ordering = ['-total_points']

    def __str__(self):
        return f"{self.register_number} - {self.total_points} points"


class Transaction(models.Model):
    user = models.ForeignKey(
        UserPoints,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    weight_grams = models.DecimalField(max_digits=8, decimal_places=2)
    points_earned = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.register_number} - {self.weight_grams}g - {self.points_earned} pts"
