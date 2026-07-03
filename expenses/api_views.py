import logging
from datetime import date, datetime, timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Expense
from .serializers import ExpenseSerializer

logger = logging.getLogger(__name__)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")
        category = self.request.query_params.get("category")
        if year and month:
            qs = qs.filter(date__year=year, date__month=month)
        if category:
            qs = qs.filter(category=category)
        return qs

    @action(detail=False, methods=["get"])
    def stats(self, request):
        now = timezone.localtime(timezone.now())
        today_start = timezone.make_aware(datetime.combine(now.date(), datetime.min.time()))
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        today_qs = Expense.objects.filter(date=now.date())
        week_qs = Expense.objects.filter(date__gte=week_start.date(), date__lte=now.date())
        month_qs = Expense.objects.filter(date__gte=month_start.date(), date__lte=now.date())

        today_total = today_qs.aggregate(t=Sum("amount"))["t"] or 0
        week_total = week_qs.aggregate(t=Sum("amount"))["t"] or 0
        month_total = month_qs.aggregate(t=Sum("amount"))["t"] or 0

        recent = Expense.objects.all()[:5]

        categories = dict(Expense.CATEGORY_CHOICES)
        cat_totals = {}
        for key, _ in categories.items():
            val = Expense.objects.filter(
                date__gte=month_start.date(), date__lte=now.date(), category=key
            ).aggregate(t=Sum("amount"))["t"]
            if val:
                cat_totals[key] = val

        data = {
            "today_total": today_total,
            "week_total": week_total,
            "month_total": month_total,
            "recent_expenses": ExpenseSerializer(recent, many=True).data,
            "category_breakdown": cat_totals,
        }
        return Response(data)

    @action(detail=False, methods=["post"])
    def upload_receipt(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
        mime_type = image.content_type or "image/jpeg"
        image_bytes = image.read()
        try:
            from llm_extraction.extractor import extract_receipt

            result = extract_receipt(image_bytes, mime_type)
        except Exception:
            logger.exception("LLM extraction error")
            result = None

        if not result:
            return Response({"extracted": None, "message": "Could not extract from receipt. Please enter details manually."})
        return Response({"extracted": result})
