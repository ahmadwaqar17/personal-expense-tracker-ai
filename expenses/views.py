import json
import logging
from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Expense

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "admin@kharchatrack.com"
ADMIN_PASSWORD = "kharcha123"


def _login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("logged_in"):
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper


def login_view(request):
    if request.session.get("logged_in"):
        return redirect("dashboard")
    error = None
    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session["logged_in"] = True
            request.session["email"] = email
            return redirect("dashboard")
        else:
            error = "Invalid email or password."
    return render(request, "expenses/login.html", {"error": error})


def logout_view(request):
    request.session.flush()
    return redirect("login")


@require_http_methods(["GET"])
@_login_required
def dashboard(request):
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

    cat_totals = {}
    for key, _ in Expense.CATEGORY_CHOICES:
        val = Expense.objects.filter(
            date__gte=month_start.date(), date__lte=now.date(), category=key
        ).aggregate(t=Sum("amount"))["t"]
        if val:
            cat_totals[key] = float(val)

    ctx = {
        "today_total": today_total,
        "week_total": week_total,
        "month_total": month_total,
        "recent_expenses": recent,
        "category_breakdown_json": json.dumps(cat_totals),
    }
    return render(request, "expenses/dashboard.html", ctx)


@require_http_methods(["GET", "POST"])
@_login_required
def upload_receipt(request):
    result = None
    error = None
    if request.method == "POST":
        image = request.FILES.get("image")
        if not image:
            error = "Please select an image to upload."
        else:
            mime_type = image.content_type or "image/jpeg"
            image_bytes = image.read()
            try:
                from llm_extraction.extractor import extract_receipt

                result = extract_receipt(image_bytes, mime_type)
            except Exception:
                logger.exception("LLM extraction error")
                result = None
            if not result:
                error = "Could not extract details from the receipt. Please enter them manually."
    now_local = timezone.localtime(timezone.now())
    ctx = {
        "extracted": result,
        "error": error,
        "today": now_local.date().isoformat(),
        "now": now_local.strftime("%H:%M"),
    }
    return render(request, "expenses/upload_receipt.html", ctx)


@require_http_methods(["GET", "POST"])
@_login_required
def manual_entry(request):
    now_local = timezone.localtime(timezone.now())
    saved = False
    if request.method == "POST":
        Expense.objects.create(
            date=request.POST.get("date") or now_local.date(),
            time=request.POST.get("time") or now_local.strftime("%H:%M"),
            amount=request.POST.get("amount", 0),
            merchant=request.POST.get("merchant", ""),
            category=request.POST.get("category", "Other"),
            description=request.POST.get("description", ""),
            source="manual",
        )
        saved = True
    ctx = {
        "saved": saved,
        "today": now_local.date().isoformat(),
        "now": now_local.strftime("%H:%M"),
    }
    return render(request, "expenses/manual_entry.html", ctx)


@require_http_methods(["GET"])
@_login_required
def expense_list(request):
    qs = Expense.objects.all()
    year = request.GET.get("year")
    month = request.GET.get("month")
    category = request.GET.get("category")
    if year:
        qs = qs.filter(date__year=year)
    if month:
        qs = qs.filter(date__month=month)
    if category:
        qs = qs.filter(category=category)

    now_local = timezone.localtime(timezone.now())
    year_range = sorted(set(Expense.objects.values_list("date__year", flat=True)))
    if not year_range:
        year_range = [now_local.year]

    ctx = {
        "expenses": qs,
        "categories": dict(Expense.CATEGORY_CHOICES),
        "year_range": year_range,
        "selected_year": year,
        "selected_month": month,
        "selected_category": category,
    }
    return render(request, "expenses/expense_list.html", ctx)


@require_http_methods(["POST"])
@_login_required
def delete_expense(request, expense_id):
    Expense.objects.filter(id=expense_id).delete()
    return redirect("expense_list")


@require_http_methods(["POST"])
@_login_required
def save_from_receipt(request):
    if request.method == "POST":
        Expense.objects.create(
            date=request.POST.get("date") or date.today(),
            time=request.POST.get("time") or datetime.now().strftime("%H:%M"),
            amount=request.POST.get("amount", 0),
            merchant=request.POST.get("merchant", ""),
            category=request.POST.get("category", "Other"),
            description=request.POST.get("description", ""),
            source="receipt",
        )
    return redirect("dashboard")
