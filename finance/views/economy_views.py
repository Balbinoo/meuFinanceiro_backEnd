import datetime
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import Q , Sum, Count
from ..models import Account, Expense
from django.db.models import DecimalField
from decimal import Decimal


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_total_balance_filtered(request):

    account = request.query_params.get("account")

    accounts = Account.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    )

    if account:
        accounts = accounts.filter(name=account)

    total = accounts.aggregate(
        total_balance=Sum("balance")
    )

    return Response({
        "total_balance": total["total_balance"] or 0
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_top_expenses(request):
    account = request.query_params.get("account")
    periods = request.query_params.get("periods")

    expenses = Expense.objects.filter(
        user=request.user,
        deleted_at__isnull=True,
    ).exclude(store="").exclude(store__isnull=True)

    # Filtro por conta
    if account:
        expenses = expenses.filter(account__name=account)

    # Filtro por períodos
    if periods:
        period_filters = Q()

        try:
            for selected_period in periods.split(","):
                selected_date = datetime.strptime(
                    selected_period.strip(),
                    "%B %Y",
                )

                period_filters |= Q(
                    date__year=selected_date.year,
                    date__month=selected_date.month,
                )

            expenses = expenses.filter(period_filters)

        except ValueError:
            return Response(
                {"error": "Invalid period. Use Month YYYY."},
                status=400,
            )

    # Agrupamento por estabelecimento e categoria
    top_expenses = (
        expenses
        .values("store", "category")
        .annotate(
            total_amount=Sum("amount"),
            frequency=Count("id"),
        )
        .order_by("-total_amount")[:5]
    )

    return Response({
        "top_expenses": list(top_expenses)
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_expense_categories_filter(request):
    account = request.query_params.get("account")
    periods = request.query_params.get("periods")

    expenses = Expense.objects.filter(
        user=request.user,
        deleted_at__isnull=True,
    )

    # Filtro por conta
    if account:
        expenses = expenses.filter(account__name=account)

    # Filtro por períodos
    if periods:
        period_filters = Q()

        try:
            for selected_period in periods.split(","):
                selected_date = datetime.strptime(
                    selected_period.strip(),
                    "%B %Y",
                )

                period_filters |= Q(
                    date__year=selected_date.year,
                    date__month=selected_date.month,
                )

            expenses = expenses.filter(period_filters)

        except ValueError:
            return Response(
                {"error": "Invalid period. Use Month YYYY."},
                status=400,
            )

    # Total monetário de todas as despesas filtradas
    total_expenses = expenses.aggregate(
        total=Coalesce(
            Sum("amount"),
            Decimal("0.00"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
    )["total"]

    # Agrupa por categoria
    categories = (
        expenses
        .values("category")
        .annotate(
            count=Count("id"),
            total_amount=Sum("amount"),
        )
        .order_by("-total_amount")
    )

    categories_data = []

    for item in categories:
        amount = item["total_amount"] or Decimal("0.00")

        percentage = (
            (amount / total_expenses) * 100
            if total_expenses > 0
            else Decimal("0.00")
        )

        categories_data.append({
            "category": item["category"],
            "count": item["count"],
            "total_amount": amount,
            "percentage": round(percentage, 2),
        })

    return Response({
        "total_expenses": total_expenses,
        "categories": categories_data,
    })