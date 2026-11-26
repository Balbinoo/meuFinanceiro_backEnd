import datetime
import calendar
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F, Value, CharField, Sum, Count
from ..models import Account, Income, Expense
from django.utils import timezone

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getIncomeFiltered(request):

    periods = request.query_params.get("periods")
    account = request.query_params.get("account")

    incomes = Income.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    )

    if account:
            incomes = incomes.filter(account__name=account)

    if periods:
        period_filters = Q()

        try:
            for selected_period in periods.split(","):
                selected_date = datetime.strptime(
                    selected_period.strip(),
                    "%B %Y"
                )

                period_filters |= Q(
                    date__year=selected_date.year,
                    date__month=selected_date.month
                )

            incomes = incomes.filter(period_filters)

        except ValueError:
            return Response(
                {"error": "Invalid period. Use Month YYYY."},
                status=400
            )

    totals = incomes.aggregate(
        total=Sum("amount"),
        counted=Count("amount")
    )

    return Response({
        "total_income": totals["total"] or 0,
        "counted": totals["counted"]
    })



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getExpenseFiltered(request):

    periods = request.query_params.get("periods")
    account = request.query_params.get("account")

    expenses = Expense.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    )

    if account:
            expenses = expenses.filter(account__name=account)

    if periods:
        period_filters = Q()

        try:
            for selected_period in periods.split(","):
                selected_date = datetime.strptime(
                    selected_period.strip(),
                    "%B %Y"
                )

                period_filters |= Q(
                    date__year=selected_date.year,
                    date__month=selected_date.month
                )

            expenses = expenses.filter(period_filters)

        except ValueError:
            return Response(
                {"error": "Invalid period. Use Month YYYY."},
                status=400
            )

    totals = expenses.aggregate(
        total=Sum("amount"),
        counted=Count("amount")
    )

    return Response({
        "total_expense": totals["total"] or 0,
        "counted": totals["counted"]
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllTransactions(request):

    category = request.query_params.get("category")
    account = request.query_params.get("account")
    period = request.query_params.get("period")
    search = request.query_params.get("search")
    ordering = request.query_params.get("ordering")
    transaction_type = request.query_params.get("transaction_type")
    periods = request.query_params.get("periods")

    incomes = (
        Income.objects
        .filter(
            user=request.user,
            deleted_at__isnull=True
        )
        .order_by()
        .annotate(
            transaction_type=Value(
                "income",
                output_field=CharField()
            ),
            description=F("origin"),
        )
        .values(
            "transaction_type",
            "description",
            "category",
            "type",
            "date",
            "amount",
            account_name=F("account__name"),
        )
    )

    expenses = (
        Expense.objects
        .filter(
            user=request.user,
            deleted_at__isnull=True,
        )
        .order_by()
        .annotate(
            transaction_type=Value(
                "expense",
                output_field=CharField()
            ),
            description=F("store"),
        )
        .values(
            "transaction_type",
            "description",
            "category",
            "type",
            "date",
            "amount",
            account_name=F("account__name"),
        )
    )

    if category:
            incomes = incomes.filter(category=category)
            expenses = expenses.filter(category=category)

    if account:
            incomes = incomes.filter(account__name=account)
            expenses = expenses.filter(account__name=account)

    if period:
        try:
            selected_date = datetime.strptime(period, "%B %Y")
            incomes = incomes.filter(
                date__year=selected_date.year,
                date__month=selected_date.month
            )
            expenses = expenses.filter(
                date__year=selected_date.year,
                date__month=selected_date.month
            )
        except ValueError:
            return Response(
                {"error": "Invalid period. Use Month YYYY."},
                status=400
            )

    if search:
        incomes = incomes.filter(
             Q(origin__icontains=search) |
             Q(category__icontains=search) |
             Q(account__name__icontains=search)
        )
        expenses = expenses.filter(
            Q(store__icontains=search) |
            Q(name__icontains=search) |
            Q(category__icontains=search) |
            Q(account__name__icontains=search)
        )

    if transaction_type == "income":
            expenses = expenses.none()

    elif transaction_type == "expense":
            incomes = incomes.none()

    if periods:
        period_filters = Q()
        try:
            for selected_period in periods.split(","):
                selected_date = datetime.strptime(
                    selected_period.strip(),
                    "%B %Y"
               )

                period_filters |= Q(
                   date__year=selected_date.year,
                   date__month=selected_date.month
               )

            incomes = incomes.filter(period_filters)
            expenses = expenses.filter(period_filters)
        except ValueError:
            return Response(
                {"error": "Invalid period. Use Month YYYY."},
                status=400
            )

    ordering_options = {
         "newest": "-date",
         "oldest": "date",
         "↑ Price": "-amount",
         "↓ Price": "amount"
    }
    
    transactions = incomes.union(
        expenses,
        all=True
    ).order_by(ordering_options.get(ordering,"-date"))

    paginator = PageNumberPagination()
    paginator.page_size = 10

    page = paginator.paginate_queryset(
        transactions,
        request
    )

    return paginator.get_paginated_response(page)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_accounts_list(request):
    accounts_list = Account.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).values_list("name",flat=True)
    return Response({
        "accounts_list": list(accounts_list)
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_last_five_months(request):
    today = timezone.localdate()

    last_five_months = []

    for offset in range(4, -1, -1):
        month_index = today.month - offset
        month_year = today.year

        while month_index < 1:
            month_index += 12
            month_year -= 1

        last_five_months.append(
            f"{calendar.month_name[month_index]} {month_year}"
        )
        
    return Response({"last_five_months": last_five_months[::-1]})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_categories(request):
    expense_categories = (
        Expense.objects
        .filter(
            user=request.user,
            deleted_at__isnull=True,
            category__isnull=False,
        )
        .values_list("category", flat=True)
        .distinct()
    )

    return Response({
        "categories_list": list(expense_categories),
    })