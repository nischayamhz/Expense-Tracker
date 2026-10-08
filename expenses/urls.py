from django.urls import path
from .views import (
    register,
    dashboard,
    expense_list,
    add_expense,
    edit_expense,
    delete_expense,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('register/', register, name='register'),

    path('expenses/', expense_list, name='expense_list'),
    path('expenses/add/', add_expense, name='add_expense'),
    path('expenses/edit/<int:pk>/', edit_expense, name='edit_expense'),
    path('expenses/delete/<int:pk>/', delete_expense, name='delete_expense'),
]