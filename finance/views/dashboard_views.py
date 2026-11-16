from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.db.models import Sum

from datetime import date, timedelta

from ..models import Account, Income, Expense, Goal



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_name(request):
    return Response({
        "user_name": request.user.get_full_name() or request.user.username
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def total_balance(request):

    total = Account.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).aggregate(
        total_balance=Sum("balance")
    )

    return Response({
        "total_balance": total["total_balance"] or 0
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def total_accounts(request):

    total = Account.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).aggregate(
        total_accounts=Count("id")
    )

    return Response({
        "total_accounts": total["total_accounts"]
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_income(request):
    today = timezone.localdate()

    monthly_income = Income.objects.filter(
        user = request.user,
        deleted_at__isnull=True,
        date__month=today.month,
        date__year=today.year
    ).aggregate(total = Sum("amount"))

    return Response ({
        "monthly_income":monthly_income["total"] or 0
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_expense(request):
    today = timezone.localdate()

    monthly_expense = Expense.objects.filter(
        user = request.user,
        deleted_at__isnull=True,
        date__month=today.month,
        date__year=today.year
    ).aggregate(total = Sum("amount"))

    return Response ({        
        "monthly_expense":monthly_expense["total"] or 0
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def last_monthly_expense(request):
    today = timezone.localdate()
    last_month = today.replace(day=1) - timedelta(days=1)

    last_monthly_expense = Expense.objects.filter(
        user = request.user,
        deleted_at__isnull=True,
        date__month=last_month.month,
        date__year=last_month.year
    ).aggregate(total = Sum("amount"))

    return Response ({        
        "last_monthly_expense":last_monthly_expense["total"] or 0
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def last_monthly_income(request):
    today = timezone.localdate()
    last_month = today.replace(day=1) - timedelta(days=1)

    last_monthly_income = Income.objects.filter(
        user = request.user,
        deleted_at__isnull=True,
        date__month=last_month.month,
        date__year=last_month.year
    ).aggregate(total = Sum("amount"))

    return Response ({
        "last_monthly_income":last_monthly_income["total"] or 0
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_summary(request):
    today = timezone.localdate()

    # Primeiro dia do mês de 5 meses atrás
    month_index = today.year * 12 + today.month - 1 - 5
    start_year, start_month = divmod(month_index, 12)
    start_date = date(start_year, start_month + 1, 1)

    # Primeiro dia do próximo mês
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1)
    else:
        end_date = date(today.year, today.month + 1, 1)

    # Buscar receitas agrupadas por mês
    incomes = (
        Income.objects.filter(
            user=request.user,
            deleted_at__isnull=True,
            date__gte=start_date,
            date__lt=end_date,
        )
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
    )

    # Buscar despesas agrupadas por mês
    expenses = (
        Expense.objects.filter(
            user=request.user,
            deleted_at__isnull=True,
            date__gte=start_date,
            date__lt=end_date,
        )
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
    )

    # Transformar resultados em dicionários
    income_dict = {
        (item["month"].year, item["month"].month): float(item["total"] or 0)
        for item in incomes
    }

    expense_dict = {
        (item["month"].year, item["month"].month): float(item["total"] or 0)
        for item in expenses
    }

    # Montar os seis meses, inclusive os que não possuem transações
    data = []

    for i in range(6):
        month_index = start_year * 12 + start_month + i
        year, month = divmod(month_index, 12)
        month += 1

        data.append({
            "label": f"{month:02d}",
            "income": income_dict.get((year, month), 0),
            "expense": expense_dict.get((year, month), 0),
        })

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expense_categories(request):
    today = timezone.localdate()

    # Primeiro dia de 5 meses atrás
    month_index = today.year * 12 + today.month - 1 - 5
    start_year, start_month = divmod(month_index, 12)

    start_date = date(start_year, start_month + 1, 1)

    # Primeiro dia do próximo mês
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1)
    else:
        end_date = date(today.year, today.month + 1, 1)

    expenses = (
        Expense.objects.filter(
            user=request.user,
            deleted_at__isnull=True,
            date__gte=start_date,
            date__lt=end_date,
        )
        .values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    return Response(expenses)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recent_transactions(request):

    # Buscar as 5 receitas mais recentes
    incomes = Income.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).order_by("-date", "-id")[:5]

    # Buscar as 5 despesas mais recentes
    expenses = Expense.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).order_by("-date", "-id")[:5]

    transactions = []

    # Transformar receitas em uma estrutura padronizada
    for income in incomes:
        transactions.append({
            "id": income.id,
            "type": "income",
            "description": income.origin,
            "category": income.category,
            "amount": income.amount,
            "date": income.date,
        })

    # Transformar despesas em uma estrutura padronizada
    for expense in expenses:
        transactions.append({
            "id": expense.id,
            "type": "expense",
            "description": expense.store,
            "category": expense.category,
            "amount": expense.amount,
            "date": expense.date,
        })

    # Ordenar tudo pela data mais recente e pegar somente 5
    transactions.sort(
        key=lambda item: (item["date"], item["id"]),
        reverse=True
    )

    return Response(transactions[:5])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def goals(request):

    goals = Goal.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).values("name","saved","objective")

    return Response({
        "goals": list(goals)
    })


