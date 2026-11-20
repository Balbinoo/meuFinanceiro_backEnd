import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from decimal import Decimal
from finance.models import Account, Income, Expense, Goal

User = get_user_model()

@pytest.mark.django_db
class TestUserName:

    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
            first_name="Teste",
            last_name="Tester"
        )

        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_nome_completo_do_usuario(self):
        response = self.client.get("/api/dashboard/user_name/")

        assert response.status_code == 200
        assert response.data["user_name"] == "Teste Tester"

    def test_deve_retornar_username_se_nao_houver_nome_completo(self):
        self.user.first_name = ""
        self.user.last_name = ""
        self.user.save()

        response = self.client.get("/api/dashboard/user_name/")

        assert response.status_code == 200
        assert response.data["user_name"] == "Testes"

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/user_name/")

        assert response.status_code == 401


@pytest.mark.django_db
class TestTotalBalance:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_saldo_total(self):
        response = self.client.get("/api/dashboard/total-balance/")

        assert response.status_code == 200
        assert "total_balance" in response.data

    def test_deve_retornar_saldo_total_correto(self):
        Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )

        Account.objects.create(
            user=self.user,
            name="Poupança",
            type="Savings",
            balance=Decimal("30000.00"),
        )

        response = self.client.get("/api/dashboard/total-balance/")

        assert response.status_code == 200
        assert response.data["total_balance"] == Decimal("80000.00")

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/total-balance/")

        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestTotalAccounts:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_total_accounts(self):
        response = self.client.get("/api/dashboard/total_accounts/")

        assert response.status_code == 200
        assert "total_accounts" in response.data

    def test_deve_retornar_total_accounts_correto(self):
        Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )

        Account.objects.create(
            user=self.user,
            name="Poupança",
            type="Savings",
            balance=Decimal("30000.00"),
        )

        response = self.client.get("/api/dashboard/total_accounts/")

        assert response.status_code == 200
        assert response.data["total_accounts"] == 2

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/total_accounts/")

        assert response.status_code in [401, 403]

@pytest.mark.django_db
class TestMonthlyIncome:
       
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_monthly_income(self):
        response = self.client.get("/api/dashboard/monthly_income/")

        assert response.status_code == 200
        assert "monthly_income" in response.data

    def test_deve_retornar_monthly_income_correto(self):
        account = Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )
        Income.objects.create(
            user=self.user,
            account=account,
            origin="Enterprise",
            type="Fixed",
            category="Salary",
            amount=Decimal("10000.00"),
            date=timezone.localdate(),
        )

        response = self.client.get("/api/dashboard/monthly_income/")

        assert response.status_code == 200
        assert response.data["monthly_income"] == 10000

 
    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/monthly_income/")

        assert response.status_code in [401, 403]

@pytest.mark.django_db
class TestMonthlyExpense:
       
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_monthly_expense(self):
        response = self.client.get("/api/dashboard/monthly_expense/")

        assert response.status_code == 200
        assert "monthly_expense" in response.data

    def test_deve_retornar_monthly_expense_correto(self):
        account = Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )
        Expense.objects.create(
            user=self.user,
            account=account,
            store="McDonalds",
            name="hamburguer",
            category="Food",
            type="Variable",
            date=timezone.localdate(),
            amount=Decimal("50.00"),
        )

        response = self.client.get("/api/dashboard/monthly_expense/")

        assert response.status_code == 200
        assert response.data["monthly_expense"] == 50

 
    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/monthly_expense/")

        assert response.status_code in [401, 403]    


@pytest.mark.django_db
class TestLastMonthlyExpense:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_last_monthly_expense(self):
        response = self.client.get("/api/dashboard/last_monthly_expense/")

        assert response.status_code == 200
        assert "last_monthly_expense" in response.data
        assert response.data["last_monthly_expense"] == 0

    def test_deve_retornar_last_monthly_expense_correto(self):
        account = Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )
        last_month = timezone.localdate().replace(day=1) - timedelta(days=1)
        Expense.objects.create(
            user=self.user,
            account=account,
            store="Mercado",
            name="Compras",
            category="Food",
            type="Variable",
            date=last_month,
            amount=Decimal("75.00"),
        )
        Expense.objects.create(
            user=self.user,
            account=account,
            store="Mercado",
            name="Compras deste mês",
            category="Food",
            type="Variable",
            date=timezone.localdate(),
            amount=Decimal("25.00"),
        )

        response = self.client.get("/api/dashboard/last_monthly_expense/")

        assert response.status_code == 200
        assert response.data["last_monthly_expense"] == 75

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/last_monthly_expense/")

        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestLastMonthlyIncome:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_last_monthly_income(self):
        response = self.client.get("/api/dashboard/last_monthly_income/")

        assert response.status_code == 200
        assert "last_monthly_income" in response.data
        assert response.data["last_monthly_income"] == 0

    def test_deve_retornar_last_monthly_income_correto(self):
        account = Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )
        last_month = timezone.localdate().replace(day=1) - timedelta(days=1)
        Income.objects.create(
            user=self.user,
            account=account,
            origin="Empresa",
            type="Fixed",
            category="Salary",
            amount=Decimal("10000.00"),
            date=last_month,
        )
        Income.objects.create(
            user=self.user,
            account=account,
            origin="Empresa",
            type="Fixed",
            category="Salary",
            amount=Decimal("2000.00"),
            date=timezone.localdate(),
        )

        response = self.client.get("/api/dashboard/last_monthly_income/")

        assert response.status_code == 200
        assert response.data["last_monthly_income"] == 10000

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/last_monthly_income/")

        assert response.status_code in [401, 403]

@pytest.mark.django_db
class TestLastMonthlySummary:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_monthly_summary_vazio(self):
        response = self.client.get("/api/dashboard/monthly_summary/")

        assert response.status_code == 200
        assert len(response.data) == 6
        assert all("label" in month for month in response.data)
        assert all(month["income"] == 0 for month in response.data)
        assert all(month["expense"] == 0 for month in response.data)

    def test_deve_retornar_monthly_summary_correto(self):
        account = Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )
        last_month = timezone.localdate().replace(day=1) - timedelta(days=1)
        Income.objects.create(
            user=self.user,
            account=account,
            origin="Empresa",
            type="Fixed",
            category="Salary",
            amount=Decimal("10000.00"),
            date=last_month,
        )
        Income.objects.create(
            user=self.user,
            account=account,
            origin="Empresa",
            type="Fixed",
            category="Salary",
            amount=Decimal("2000.00"),
            date=timezone.localdate(),
        )

        response = self.client.get("/api/dashboard/monthly_summary/")

        assert response.status_code == 200
        summary_by_month = {item["label"]: item for item in response.data}
        assert summary_by_month[f"{last_month.month:02d}"]["income"] == 10000
        assert summary_by_month[f"{timezone.localdate().month:02d}"]["income"] == 2000

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/monthly_summary/")

        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestExpenseCategories:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.account = Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_categorias_de_despesas_dos_ultimos_seis_meses(self):
        today = timezone.localdate()
        month_index = today.year * 12 + today.month - 1 - 5
        start_year, start_month = divmod(month_index, 12)
        start_date = date(start_year, start_month + 1, 1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1)
        else:
            end_date = date(today.year, today.month + 1, 1)

        def create_expense(category, expense_date, deleted_at=None):
            Expense.objects.create(
                user=self.user,
                account=self.account,
                store="Loja",
                name="Compra",
                category=category,
                type="Variable",
                date=expense_date,
                amount=Decimal("10.00"),
                deleted_at=deleted_at,
            )

        create_expense("Food", start_date)
        create_expense("Food", today)
        create_expense("Transport", today)
        create_expense("Older", start_date - timedelta(days=1))
        create_expense("Future", end_date)
        create_expense("Deleted", today, timezone.now())

        response = self.client.get("/api/dashboard/expense_categories/")

        assert response.status_code == 200
        assert list(response.data) == [
            {"category": "Food", "count": 2},
            {"category": "Transport", "count": 1},
        ]

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/expense_categories/")

        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestRecentTransactions:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.account = Account.objects.create(
            user=self.user,
            name="Conta Corrente",
            type="Checking",
            balance=Decimal("50000.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_as_cinco_transacoes_mais_recentes_em_ordem(self):
        today = timezone.localdate()
        expected = []

        # Create six incomes and six expenses; matching dates are resolved by ID.
        for days_ago in range(6):
            transaction_date = today - timedelta(days=days_ago)
            income = Income.objects.create(
                user=self.user,
                account=self.account,
                origin=f"Empresa {days_ago}",
                type="Fixed",
                category="Salary",
                amount=Decimal("100.00"),
                date=transaction_date,
            )
            expense = Expense.objects.create(
                user=self.user,
                account=self.account,
                store=f"Loja {days_ago}",
                name="Compra",
                type="Variable",
                category="Food",
                amount=Decimal("25.00"),
                date=transaction_date,
            )
            expected.extend([
                (transaction_date, income.id, "income", income.origin, income.category, income.amount),
                (transaction_date, expense.id, "expense", expense.store, expense.category, expense.amount),
            ])

        expected.sort(key=lambda item: (item[0], item[1]), reverse=True)
        response = self.client.get("/api/dashboard/recent_transactions/")

        assert response.status_code == 200
        assert len(response.data) == 5
        for actual, expected_item in zip(response.data, expected[:5]):
            transaction_date, transaction_id, transaction_type, description, category, amount = expected_item
            assert actual["id"] == transaction_id
            assert actual["type"] == transaction_type
            assert actual["description"] == description
            assert actual["category"] == category
            assert Decimal(str(actual["amount"])) == amount
            assert actual["date"] == transaction_date

    def test_deve_ignorar_transacoes_excluidas_e_de_outros_usuarios(self):
        today = timezone.localdate()
        Income.objects.create(
            user=self.user,
            account=self.account,
            origin="Ativa",
            type="Fixed",
            category="Salary",
            amount=Decimal("100.00"),
            date=today,
        )
        Income.objects.create(
            user=self.user,
            account=self.account,
            origin="Excluída",
            type="Fixed",
            category="Salary",
            amount=Decimal("100.00"),
            date=today,
            deleted_at=timezone.now(),
        )
        other_user = User.objects.create_user(
            username="Outro",
            email="outro@example.com",
            password="teste12345",
        )
        other_account = Account.objects.create(
            user=other_user,
            name="Outra conta",
            type="Checking",
            balance=Decimal("0.00"),
        )
        Expense.objects.create(
            user=other_user,
            account=other_account,
            store="Outra pessoa",
            name="Compra",
            type="Variable",
            category="Food",
            amount=Decimal("10.00"),
            date=today,
        )

        response = self.client.get("/api/dashboard/recent_transactions/")

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["description"] == "Ativa"
        assert response.data[0]["type"] == "income"

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/recent_transactions/")

        assert response.status_code in [401, 403]




@pytest.mark.django_db
class TestGoals:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_goals(self):
        response = self.client.get("/api/dashboard/goals/")

        assert response.status_code == 200
        assert "goals" in response.data

    def test_deve_retornar_goals_correto(self):
        Goal.objects.create(
            user=self.user,
            name="Viagem",
            saved=Decimal("5000.00"),
            objective=Decimal("20000.00"),
        )

        response = self.client.get("/api/dashboard/goals/")

        assert response.status_code == 200
        assert len(response.data["goals"]) == 1
        goal = response.data["goals"][0]
        assert goal["name"] == "Viagem"
        assert Decimal(str(goal["saved"])) == Decimal("5000.00")
        assert Decimal(str(goal["objective"])) == Decimal("20000.00")

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/dashboard/goals/")

        assert response.status_code in [401, 403]


