from django.urls import include, path

urlpatterns = [
    path("", include("expenses.urls")),
    path("api/", include("expenses.api_urls")),
]
