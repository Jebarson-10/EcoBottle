from django.contrib import admin
from .models import UserPoints, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('weight_grams', 'points_earned', 'timestamp')


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ('register_number', 'total_points', 'created_at', 'updated_at')
    search_fields = ('register_number',)
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight_grams', 'points_earned', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__register_number',)
