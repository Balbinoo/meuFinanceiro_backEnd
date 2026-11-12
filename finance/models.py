from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # last_login já existe

class Goal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
    )
    name = models.CharField(max_length=150)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    objective = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class Income(models.Model):

    class Category(models.TextChoices):
        SALARY = "Salary", "Salary"
        DEVOLUTION = "Devolution", "Devolution"
        BONUS = "Bonus", "Bonus"
        BORROWING = "Borrowing", "Borrowing"
        FREELANCE = "Freelance", "Freelance"
        INVESTMENTS = "Investments", "Investments"
        RENTAL_INCOME = "Rental Income", "Rental Income"
        DIVIDENDS = "Dividends", "Dividends"
        INTEREST = "Interest", "Interest"
        PENSION = "Pension", "Pension"
        CASHBACK = "Cashback", "Cashback"
        GIFT = "Gift", "Gift"
        SALE = "Sale", "Sale"
        OTHER = "Other", "Other"


    class IncomeType(models.TextChoices):
        FIXED = "Fixed", "Fixed"
        VARIABLE = "Variable", "Variable"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="incomes",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="incomes",
    )
    origin = models.CharField(max_length=150)

    type = models.CharField(
        max_length=30,
        choices=IncomeType.choices,
    )

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class Expense(models.Model):

    class Category(models.TextChoices):
        FOOD = "Food", "Food"
        TRANSPORT = "Transport", "Transport"
        HOUSING = "Housing", "Housing"
        HEALTH = "Health", "Health"
        EDUCATION = "Education", "Education"
        ENTERTAINMENT = "Entertainment", "Entertainment"
        SHOPPING = "Shopping", "Shopping"
        OTHER = "Other", "Other"

    class ExpenseType(models.TextChoices):
        FIXED = "Fixed", "Fixed"
        VARIABLE = "Variable", "Variable"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="expenses",
    )

    store = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=150)

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
    )

    type = models.CharField(
        max_length=30,
        choices=ExpenseType.choices,
    )

    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    