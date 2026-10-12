
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import RegisterForm, ExpenseForm, CategoryForm
from .models import Expense, Category


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(
        request,
        'registration/register.html',
        {'form': form},
    )


@login_required
def dashboard(request):
    today = timezone.localdate()

    expenses = Expense.objects.filter(user=request.user)

    total_expenses = (
        expenses.aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    monthly_expenses = (
        expenses.filter(
            date__year=today.year,
            date__month=today.month,
        ).aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    category_totals = (
        expenses.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    recent_expenses = expenses.select_related(
        'category'
    )[:5]

    return render(
        request,
        'dashboard.html',
        {
            'total_expenses': total_expenses,
            'monthly_expenses': monthly_expenses,
            'expense_count': expenses.count(),
            'category_totals': category_totals,
            'recent_expenses': recent_expenses,
        },
    )


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(
        user=request.user
    ).select_related('category')

    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    if search:
        expenses = expenses.filter(description__icontains=search)

    categories = Category.objects.filter(user=request.user)

    if category_id:
        expenses = expenses.filter(category_id=category_id)

    if start_date:
        expenses = expenses.filter(date__gte=start_date)

    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    return render(
        request,
        'expenses/expense_list.html',
        {
            'expenses': expenses,
            'categories': categories,
            'search': search,
            'selected_category': category_id,
            'start_date': start_date,
            'end_date': end_date,
            'filtered_total': total,
        },
    )


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            messages.success(request, 'Expense added successfully.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)

    return render(
        request,
        'expenses/expense_form.html',
        {'form': form, 'page_title': 'Add Expense'},
    )


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user,
    )

    if request.method == 'POST':
        form = ExpenseForm(
            request.POST,
            instance=expense,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(
            instance=expense,
            user=request.user,
        )

    return render(
        request,
        'expenses/expense_form.html',
        {'form': form, 'page_title': 'Edit Expense'},
    )


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user,
    )

    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('expense_list')

    return render(
        request,
        'expenses/expense_confirm_delete.html',
        {'expense': expense},
    )


@login_required
def category_list(request):
    categories = Category.objects.filter(
        user=request.user
    )

    return render(
        request,
        'categories/category_list.html',
        {'categories': categories},
    )


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)

        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(user=request.user)

    return render(
        request,
        'categories/category_form.html',
        {'form': form, 'page_title': 'Add Category'},
    )


@login_required
def edit_category(request, pk):
    category = get_object_or_404(
        Category,
        pk=pk,
        user=request.user,
    )

    if request.method == 'POST':
        form = CategoryForm(
            request.POST,
            instance=category,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(
            instance=category,
            user=request.user,
        )

    return render(
        request,
        'categories/category_form.html',
        {'form': form, 'page_title': 'Edit Category'},
    )


@login_required
def delete_category(request, pk):
    category = get_object_or_404(
        Category,
        pk=pk,
        user=request.user,
    )

    if request.method == 'POST':
        if category.expenses.exists():
            messages.error(
                request,
                'This category has expenses. Reassign or delete '
                'those expenses before deleting the category.',
            )
        else:
            category.delete()
            messages.success(request, 'Category deleted successfully.')

        return redirect('category_list')

    return render(
        request,
        'categories/category_list.html',
        {
            'categories': Category.objects.filter(user=request.user),
            'delete_category': category,
        },
    )
