import os, sys, uuid
sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'expense_tracker.settings'

import django
django.setup()

from datetime import date, time
from expenses.models import Expense

data = [
    {"title": "gul", "category": "Other", "source": "manual", "amount_pkr": 4000, "date": "2026-07-03", "time": "18:29"},
    {"title": "mom", "category": "Other", "source": "manual", "amount_pkr": 10000, "date": "2026-07-03", "time": "18:28"},
    {"title": "kameeti", "category": "Other", "source": "manual", "amount_pkr": 15000, "date": "2026-07-03", "time": "18:28"},
    {"title": "CAKES & BAKES", "category": "Food", "source": "receipt", "amount_pkr": 121, "date": "2026-07-02", "time": "15:32"},
    {"title": "wokfire", "category": "Food", "source": "manual", "amount_pkr": 500, "date": "2026-07-02", "time": "01:00"},
    {"title": "elo Faisalabad PK", "category": "Shopping", "source": "receipt", "amount_pkr": 2197, "date": "2026-07-01", "time": "13:13"},
    {"title": "food", "category": "Food", "source": "manual", "amount_pkr": 320, "date": "2026-07-01", "time": "03:15"},
    {"title": "Apple Pharmacy International", "category": "Health", "source": "receipt", "amount_pkr": 1646, "date": "2026-06-30", "time": "20:36"},
    {"title": "SWERA Departmental Store", "category": "Shopping", "source": "receipt", "amount_pkr": 1244, "date": "2026-06-29", "time": "20:52"},
    {"title": "SWERA Departmental Store", "category": "Shopping", "source": "receipt", "amount_pkr": 1438.63, "date": "2026-06-29", "time": "20:47"},
]

count = 0
for item in data:
    Expense.objects.create(
        date=item["date"],
        time=item["time"],
        amount=item["amount_pkr"],
        merchant=item["title"],
        category=item["category"],
        description="",
        source=item["source"],
    )
    count += 1
    print(f"  {count}. {item['title']} — PKR {item['amount_pkr']} [{item['category']}]")

print(f"\nDone. {count} expenses imported.")
