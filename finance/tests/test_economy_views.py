import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from finance.models import Account, Expense
from datetime import date

User = get_user_model()

@pytest.mark.django_db
class TestGetTotalBalanceFiltered:

    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )

        self.client.force_authenticate(user=self.user)

        self.account1 = Account.objects.create(
            user=self.user,
            name="Banco do Brasil",
            type="Banco",
            balance=10000,
        )

        self.account2 = Account.objects.create(
            user=self.user,
            name="Nubank",
            type="Banco",
            balance=5000,
        )

    def test_should_return_total_balance_of_authenticated_user(self):
        response = self.client.get("/api/economy/balance_filtered/")

        assert response.status_code == 200
        assert response.data == {
            "total_balance": Decimal("15000.00")
        }

    def test_should_return_balance_filtered_by_account(self):
        response = self.client.get(
            "/api/economy/balance_filtered/",
            {"account": "Banco do Brasil"},
        )

        assert response.status_code == 200
        assert response.data == {
            "total_balance": Decimal("10000.00")
        }

    def test_should_return_zero_when_user_has_no_accounts(self):
        Account.objects.filter(user=self.user).delete()

        response = self.client.get("/api/economy/balance_filtered/")

        assert response.status_code == 200
        assert response.data == {
            "total_balance": 0
        }

    def test_should_not_return_balance_from_another_user(self):
        another_user = User.objects.create_user(
            username="OutroUsuario",
            email="outro.usuario@example.com",
            password="teste12345",
        )

        Account.objects.create(
            user=another_user,
            name="Conta de outro usuário",
            type="Banco",
            balance=80000,
        )

        response = self.client.get("/api/economy/balance_filtered/")

        assert response.status_code == 200
        assert response.data == {
            "total_balance": Decimal("15000.00")
        }

    def test_should_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/economy/balance_filtered/")

        assert response.status_code == 401

@pytest.mark.django_db
class TestGetTopExpenses:

    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="Testes",
            email="outro.usuario@example.com",
            password="teste12345",
        )

        self.client.force_authenticate(user=self.user)

        self.account = Account.objects.create(
            user=self.user,
            name="Banco do Brasil",
            type="Banco",
            balance=10000,
        )

        self.account2 = Account.objects.create(
            user=self.user,
            name="Nubank",
            type="Banco",
            balance=5000,
        )

        # Supermercado: 3 despesas, total R$ 1.500
        self.create_expense(
            store="Supermercado",
            category="Food",
            amount=500,
            expense_date=date(2026, 9, 10),
        )

        self.create_expense(
            store="Supermercado",
            category="Food",
            amount=700,
            expense_date=date(2026, 9, 15),
        )

        self.create_expense(
            store="Supermercado",
            category="Food",
            amount=300,
            expense_date=date(2026, 10, 5),
        )

        # Posto: 2 despesas, total R$ 400
        self.create_expense(
            store="Posto",
            category="Transport",
            amount=200,
            expense_date=date(2026, 9, 12),
        )

        self.create_expense(
            store="Posto",
            category="Transport",
            amount=200,
            expense_date=date(2026, 9, 20),
        )

        # Farmácia: 1 despesa, total R$ 250
        self.create_expense(
            store="Farmácia",
            category="Health",
            amount=250,
            expense_date=date(2026, 10, 10),
        )

    def create_expense(
        self,
        store,
        category,
        amount,
        expense_date,
        account=None,
    ):
        return Expense.objects.create(
            user=self.user,
            account=account or self.account,
            store=store,
            name=store,
            category=category,
            type="Variable",
            amount=Decimal(str(amount)),
            date=expense_date,
        )

    def test_should_return_top_expenses_grouped_by_store_and_category(self):
        response = self.client.get(
            "/api/economy/top_expenses/"
        )

        assert response.status_code == 200

        assert response.data["top_expenses"] == [
            {
                "store": "Supermercado",
                "category": "Food",
                "total_amount": Decimal("1500.00"),
                "frequency": 3,
            },
            {
                "store": "Posto",
                "category": "Transport",
                "total_amount": Decimal("400.00"),
                "frequency": 2,
            },
            {
                "store": "Farmácia",
                "category": "Health",
                "total_amount": Decimal("250.00"),
                "frequency": 1,
            },
        ]

    def test_should_filter_expenses_by_account(self):
        self.create_expense(
            store="Restaurante",
            category="Food",
            amount=100,
            expense_date=date(2026, 9, 10),
            account=self.account2,
        )

        response = self.client.get(
            "/api/economy/top_expenses/",
            {"account": "Nubank"},
        )

        assert response.status_code == 200

        assert response.data["top_expenses"] == [
            {
                "store": "Restaurante",
                "category": "Food",
                "total_amount": Decimal("100.00"),
                "frequency": 1,
            }
        ]

    def test_should_filter_expenses_by_single_period(self):
        response = self.client.get(
            "/api/economy/top_expenses/",
            {"periods": "September 2026"},
        )

        assert response.status_code == 200

        assert response.data["top_expenses"] == [
            {
                "store": "Supermercado",
                "category": "Food",
                "total_amount": Decimal("1200.00"),
                "frequency": 2,
            },
            {
                "store": "Posto",
                "category": "Transport",
                "total_amount": Decimal("400.00"),
                "frequency": 2,
            },
        ]

    def test_should_filter_expenses_by_multiple_periods(self):
        response = self.client.get(
            "/api/economy/top_expenses/",
            {"periods": "September 2026,October 2026"},
        )

        assert response.status_code == 200

        assert response.data["top_expenses"][0] == {
            "store": "Supermercado",
            "category": "Food",
            "total_amount": Decimal("1500.00"),
            "frequency": 3,
        }

        assert len(response.data["top_expenses"]) == 3

    def test_should_filter_by_account_and_period(self):
        self.create_expense(
            store="Restaurante",
            category="Food",
            amount=100,
            expense_date=date(2026, 9, 10),
            account=self.account2,
        )

        response = self.client.get(
            "/api/economy/top_expenses/",
            {
                "account": "Nubank",
                "periods": "September 2026",
            },
        )

        assert response.status_code == 200

        assert response.data["top_expenses"] == [
            {
                "store": "Restaurante",
                "category": "Food",
                "total_amount": Decimal("100.00"),
                "frequency": 1,
            }
        ]


    def test_should_not_return_expenses_from_another_user(self):
        another_user = User.objects.create_user(
            username="OutroUsuario",
            password="teste12345",
        )

        another_account = Account.objects.create(
            user=another_user,
            name="Outra conta",
            type="Banco",
            balance=80000,
        )

        Expense.objects.create(
            user=another_user,
            account=another_account,
            store="Loja de outro usuário",
            name="Compra",
            category="Shopping",
            type="Variable",
            amount=Decimal("9000.00"),
            date=date(2026, 9, 10),
        )

        response = self.client.get(
            "/api/economy/top_expenses/"
        )

        assert response.status_code == 200

        stores = [
            item["store"]
            for item in response.data["top_expenses"]
        ]

        assert "Loja de outro usuário" not in stores

    def test_should_return_at_most_five_results(self):
        for index in range(6):
            self.create_expense(
                store=f"Loja {index}",
                category="Shopping",
                amount=1000 + index,
                expense_date=date(2026, 9, 10),
            )

        response = self.client.get(
            "/api/economy/top_expenses/"
        )

        assert response.status_code == 200
        assert len(response.data["top_expenses"]) == 5

    def test_should_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/economy/top_expenses/"
        )

        assert response.status_code == 401

@pytest.mark.django_db
class TestGetExpenseCategoriesFilter:

    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="Testes",
            email="outro.usuario@example.com",
            password="teste12345",
        )

        self.client.force_authenticate(user=self.user)

        self.account = Account.objects.create(
            user=self.user,
            name="Banco do Brasil",
            type="Banco",
            balance=10000,
        )

        self.account2 = Account.objects.create(
            user=self.user,
            name="Nubank",
            type="Banco",
            balance=5000,
        )

        # Food: 3 despesas, total R$ 1.500
        self.create_expense(
            category="Food",
            amount=500,
            expense_date=date(2026, 9, 10),
        )

        self.create_expense(
            category="Food",
            amount=700,
            expense_date=date(2026, 9, 15),
        )

        self.create_expense(
            category="Food",
            amount=300,
            expense_date=date(2026, 10, 5),
        )

        # Transport: 2 despesas, total R$ 400
        self.create_expense(
            category="Transport",
            amount=200,
            expense_date=date(2026, 9, 12),
        )

        self.create_expense(
            category="Transport",
            amount=200,
            expense_date=date(2026, 10, 20),
        )

        # Health: 1 despesa, total R$ 100
        self.create_expense(
            category="Health",
            amount=100,
            expense_date=date(2026, 10, 10),
        )

    def create_expense(
        self,
        category,
        amount,
        expense_date,
        account=None,
    ):
        return Expense.objects.create(
            user=self.user,
            account=account or self.account,
            store="Estabelecimento",
            name="Despesa de teste",
            category=category,
            type="Variable",
            amount=Decimal(str(amount)),
            date=expense_date,
        )

    def test_should_return_all_expense_categories(self):
        response = self.client.get(
            "/api/economy/expense_categories/"
        )

        assert response.status_code == 200

        assert response.data["total_expenses"] == Decimal("2000.00")

        assert response.data["categories"] == [
            {
                "category": "Food",
                "count": 3,
                "total_amount": Decimal("1500.00"),
                "percentage": Decimal("75.00"),
            },
            {
                "category": "Transport",
                "count": 2,
                "total_amount": Decimal("400.00"),
                "percentage": Decimal("20.00"),
            },
            {
                "category": "Health",
                "count": 1,
                "total_amount": Decimal("100.00"),
                "percentage": Decimal("5.00"),
            },
        ]

    def test_should_filter_expenses_by_account(self):
        self.create_expense(
            category="Shopping",
            amount=300,
            expense_date=date(2026, 9, 10),
            account=self.account2,
        )

        response = self.client.get(
            "/api/economy/expense_categories/",
            {"account": "Nubank"},
        )

        assert response.status_code == 200

        assert response.data["total_expenses"] == Decimal("300.00")

        assert response.data["categories"] == [
            {
                "category": "Shopping",
                "count": 1,
                "total_amount": Decimal("300.00"),
                "percentage": Decimal("100.00"),
            }
        ]

    def test_should_filter_expenses_by_single_period(self):
        response = self.client.get(
            "/api/economy/expense_categories/",
            {"periods": "September 2026"},
        )

        assert response.status_code == 200

        assert response.data["total_expenses"] == Decimal("1400.00")

        assert response.data["categories"] == [
            {
                "category": "Food",
                "count": 2,
                "total_amount": Decimal("1200.00"),
                "percentage": Decimal("85.71"),
            },
            {
                "category": "Transport",
                "count": 1,
                "total_amount": Decimal("200.00"),
                "percentage": Decimal("14.29"),
            },
        ]

    def test_should_filter_expenses_by_multiple_periods(self):
        response = self.client.get(
            "/api/economy/expense_categories/",
            {"periods": "September 2026,October 2026"},
        )

        assert response.status_code == 200

        assert response.data["total_expenses"] == Decimal("2000.00")
        assert len(response.data["categories"]) == 3

    def test_should_filter_by_account_and_period(self):
        self.create_expense(
            category="Shopping",
            amount=300,
            expense_date=date(2026, 9, 10),
            account=self.account2,
        )

        response = self.client.get(
            "/api/economy/expense_categories/",
            {
                "account": "Nubank",
                "periods": "September 2026",
            },
        )

        assert response.status_code == 200

        assert response.data["total_expenses"] == Decimal("300.00")

        assert response.data["categories"] == [
            {
                "category": "Shopping",
                "count": 1,
                "total_amount": Decimal("300.00"),
                "percentage": Decimal("100.00"),
            }
        ]


    def test_should_not_return_expenses_from_another_user(self):
        another_user = User.objects.create_user(
            username="OutroUsuario",
            password="teste12345",
        )

        another_account = Account.objects.create(
            user=another_user,
            name="Outra conta",
            type="Banco",
            balance=80000,
        )

        Expense.objects.create(
            user=another_user,
            account=another_account,
            store="Outra loja",
            name="Compra de outro usuário",
            category="Shopping",
            type="Variable",
            amount=Decimal("9000.00"),
            date=date(2026, 9, 10),
        )

        response = self.client.get(
            "/api/economy/expense_categories/"
        )

        assert response.status_code == 200

        assert response.data["total_expenses"] == Decimal("2000.00")

        categories = [
            item["category"]
            for item in response.data["categories"]
        ]

        assert "Shopping" not in categories

    def test_should_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/economy/expense_categories/"
        )

        assert response.status_code == 401
