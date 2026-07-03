from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("upload/", views.upload_receipt, name="upload_receipt"),
    path("add/", views.manual_entry, name="manual_entry"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/<uuid:expense_id>/delete/", views.delete_expense, name="delete_expense"),
    path("save-receipt/", views.save_from_receipt, name="save_from_receipt"),
]
