from rest_framework.routers import DefaultRouter
from django.urls import path, include
from finance.views.dashboard_views import last_monthly_expense, last_monthly_income
from .views._init_ import ExpenseViewSet, IncomeViewSet, GoalViewSet, AccountViewSet, UserViewSet, RegisterView, total_balance, monthly_income, monthly_expense, monthly_summary, expense_categories, recent_transactions, goals,total_accounts,user_name
from finance.views.transactions_view import  get_all_categories, getAllTransactions, get_accounts_list,get_last_five_months

router = DefaultRouter()
router.register("expenses", ExpenseViewSet, basename="expense")
router.register("incomes", IncomeViewSet, basename="income")
router.register("goals", GoalViewSet, basename="goal")
router.register("accounts", AccountViewSet, basename="account")
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("",include(router.urls)),

    path("register/", RegisterView.as_view(), name="register"),

    path("dashboard/total-balance/", total_balance, name="total_balance"),
    path("dashboard/monthly_income/", monthly_income, name="monthly_income"),
    path("dashboard/monthly_expense/", monthly_expense, name="monthly_expense"),
    path("dashboard/monthly_summary/", monthly_summary, name="monthly_summary"),
    path("dashboard/expense_categories/", expense_categories, name="expense_categories"),
    path("dashboard/recent_transactions/",recent_transactions,name="recent_transactions"), 
    path("dashboard/goals/",goals,name="goals"),
    path("dashboard/last_monthly_expense/",last_monthly_expense,name="last_monthly_expense"),
    path("dashboard/last_monthly_income/",last_monthly_income,name="last_monthly_income"),
    path("dashboard/total_accounts/",total_accounts,name="total_accounts"),
    path("dashboard/user_name/",user_name,name="user_name"),

    path("transactions/all/",getAllTransactions,name="AllTransactions"),
    path("transactions/accounts_list/",get_accounts_list,name="accounts_list"),
    path("transactions/last_five_months/", get_last_five_months,name="get_last_five_months"),
    path("transactions/all_categories/", get_all_categories,name="all_categories")
]

# it created the whole set of requests from this
#urlpatterns = router.urls