from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import ExpenseViewSet

router = DefaultRouter()
router.register(r"expenses", ExpenseViewSet, basename="api-expenses")

urlpatterns = [
    path("", include(router.urls)),
]
