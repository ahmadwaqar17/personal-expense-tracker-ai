from rest_framework import serializers

from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "date",
            "time",
            "amount",
            "currency",
            "merchant",
            "category",
            "description",
            "source",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ExpenseStatsSerializer(serializers.Serializer):
    today_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    week_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    month_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    recent_expenses = ExpenseSerializer(many=True)
    category_breakdown = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
