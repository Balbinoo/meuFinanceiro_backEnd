from rest_framework.permissions import IsAuthenticated
from django.db.models import F,Value, CharField
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from ..models import Income, Expense

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