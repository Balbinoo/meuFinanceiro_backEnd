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
def total_balance_filtered(request):

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