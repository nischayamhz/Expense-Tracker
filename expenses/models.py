
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expense_categories'
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_category_name_per_user'
            )
        ]

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    description = models.TextField()
    date = models.DateField()

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.category.name} - {self.amount}'
