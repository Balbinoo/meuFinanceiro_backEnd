from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import F,Value, CharField
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from ..models import Account, Income, Expense
from django.utils import timezone

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllTransactions(request):
    incomes = (
        Income.objects
        .filter(
            user=request.user,
            deleted_at__isnull=True
        )
        .order_by()
        .annotate(
            transaction_type = Value(
                "income",
                output_field = CharField()
            ),
            description = F("origin")
        )
        .values(
            "transaction_type",
            "description",
            "category",
            "type",
            "date",
            "amount",
            "account_id",
        )
    )    
    expenses = (
        Expense.objects
        .filter(
            user=request.user,
            deleted_at__isnull=True
        )
        .order_by()
        .annotate(
            transaction_type=Value(
                "expense",
                output_field=CharField()
            ),
            description=F("store")
        )
        .values(
            "transaction_type",
            "description",
            "category",
            "type",
            "date",
            "amount",
            "account_id",
        )
    )
    #combina incomes e expenses
    transactions = incomes.union(
        expenses,
        all=True
    ).order_by(
        "-date",
    )
    #pagination
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
    month_names = (
        "January", "February", "March", "April", "May", "June","July", "August","September","October", "November", "December",
    )

    today = timezone.localdate()
    year = today.year
    month = today.month
    last_five_months = []

    for offset in range(4, -1, -1):
        month_index = month - offset
        month_year = year

        if month_index < 1:
            month_index += 12
            month_year -= 1

        last_five_months.append(month_names[month_index - 1])

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