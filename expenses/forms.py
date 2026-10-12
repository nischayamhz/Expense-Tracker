
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Expense, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if self.user:
            categories = Category.objects.filter(
                user=self.user,
                name__iexact=name,
            )

            if self.instance.pk:
                categories = categories.exclude(
                    pk=self.instance.pk
                )

            if categories.exists():
                raise forms.ValidationError(
                    'You already have a category with this name.'
                )

        return name


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category',
            'amount',
            'description',
            'date',
        ]
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 3}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['category'].queryset = (
            Category.objects.filter(user=user)
            if user is not None
            else Category.objects.none()
        )

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount <= 0:
            raise forms.ValidationError(
                'Amount must be greater than zero.'
            )

        return amount

    def clean_category(self):
        category = self.cleaned_data['category']

        if self.user and category.user_id != self.user.id:
            raise forms.ValidationError(
                'Please select one of your own categories.'
            )

        return category
