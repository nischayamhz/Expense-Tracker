from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ExpenseForm
from .models import Expense


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form.html', {'form': form})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/expense_form.html', {'form': form})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')

    return render(
        request,
        'expenses/expense_confirm_delete.html',
        {'expense': expense}
    )