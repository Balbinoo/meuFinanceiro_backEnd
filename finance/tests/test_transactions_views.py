import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from decimal import Decimal
from finance.models import Account, Income, Expense, Goal

User = get_user_model()

@pytest.mark.django_db
class TestGetAllTransactions:
    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )

        self.account = Account.objects.create(
            user=self.user,
            name="Nubank",
            type="Banco",
            balance=10000,
        )

        self.client.force_authenticate(user=self.user)

    def criar_income(
        self,
        amount=1000,
        income_date=date(2026, 11, 10),
        category="Salary",
        account=None,
        user=None,
        origin="Empresa",
        deleted_at=None,
    ):
        user = user or self.user
        account = account or self.account

        return Income.objects.create(
            user=user,
            account=account,
            origin=origin,
            type="Fixed",
            category=category,
            amount=amount,
            date=income_date,
            deleted_at=deleted_at,
        )

    def criar_expense(
        self,
        amount=100,
        expense_date=date(2026, 11, 10),
        category="Food",
        account=None,
        user=None,
        store="Restaurante",
        name="Almoço",
        deleted_at=None,
    ):
        user = user or self.user
        account = account or self.account

        return Expense.objects.create(
            user=user,
            account=account,
            store=store,
            name=name,
            category=category,
            type="Variable",
            amount=amount,
            date=expense_date,
            deleted_at=deleted_at,
        )

        # TESTES BÁSICOS

    def test_deve_retornar_all_transactions(self):
        self.criar_income()
        self.criar_expense()

        response = self.client.get(
            "/api/transactions/all/"
        )

        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
        assert response.data["count"] == 2

    def test_deve_retornar_receitas_e_despesas(self):
        self.criar_income()
        self.criar_expense()

        response = self.client.get(
            "/api/transactions/all/"
        )

        transactions = response.data["results"]

        transaction_types = [
            transaction["transaction_type"]
            for transaction in transactions
        ]

        assert "income" in transaction_types
        assert "expense" in transaction_types

    def test_deve_filtrar_por_categoria(self):
        self.criar_expense(category="Food")
        self.criar_expense(category="Transport")

        response = self.client.get(
            "/api/transactions/all/",
            {"category": "Food"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["category"] == "Food"

    def test_deve_filtrar_por_conta(self):
        outra_conta = Account.objects.create(
            user=self.user,
            name="Inter",
            type="Banco",
            balance=5000,
        )

        self.criar_income()
        self.criar_expense(account=outra_conta)

        response = self.client.get(
            "/api/transactions/all/",
            {"account": "Inter"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["account_name"] == "Inter"


    def test_deve_filtrar_por_periodo(self):
        self.criar_income(
            income_date=date(2026, 11, 10)
        )

        self.criar_expense(
            expense_date=date(2026, 10, 10)
        )

        response = self.client.get(
            "/api/transactions/all/",
            {"period": "November 2026"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1


    def test_deve_filtrar_por_search(self):
        self.criar_income(origin="Empresa ABC")
        self.criar_expense(store="Supermercado")

        response = self.client.get(
            "/api/transactions/all/",
            {"search": "Supermercado"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert (
            response.data["results"][0]["description"]
            == "Supermercado"
        )

    
    def test_deve_retornar_apenas_incomes(self):
        self.criar_income()
        self.criar_expense()

        response = self.client.get(
            "/api/transactions/all/",
            {"transaction_type": "income"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert (
            response.data["results"][0]["transaction_type"]
            == "income"
        )


    def test_deve_retornar_apenas_expenses(self):
        self.criar_income()
        self.criar_expense()

        response = self.client.get(
            "/api/transactions/all/",
            {"transaction_type": "expense"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert (
            response.data["results"][0]["transaction_type"]
            == "expense"
        )

    def test_deve_filtrar_por_varios_periodos(self):
        self.criar_income(
            income_date=date(2026, 11, 10)
        )

        self.criar_expense(
            expense_date=date(2026, 10, 10)
        )

        self.criar_expense(
            expense_date=date(2026, 9, 10)
        )

        self.criar_income(
            income_date=date(2026, 8, 10)
        )

        response = self.client.get(
            "/api/transactions/all/",
            {
                "periods": "November 2026,October 2026"
            },
        )

        assert response.status_code == 200
        assert response.data["count"] == 2


    def test_deve_ordenar_por_data_mais_recente(self):
        self.criar_income(
            income_date=date(2026, 11, 5)
        )

        self.criar_expense(
            expense_date=date(2026, 11, 20)
        )

        response = self.client.get(
            "/api/transactions/all/",
            {"ordering": "newest"},
        )

        results = response.data["results"]

        assert results[0]["date"] == date(2026, 11, 20)
        assert results[1]["date"] == date(2026, 11, 5)

    def test_deve_ordenar_por_data_mais_antiga(self):
        self.criar_income(
            income_date=date(2026, 11, 5)
        )

        self.criar_expense(
            expense_date=date(2026, 11, 20)
        )

        response = self.client.get(
            "/api/transactions/all/",
            {"ordering": "oldest"},
        )

        results = response.data["results"]

        assert results[0]["date"] == date(2026, 11, 5)
        assert results[1]["date"] == date(2026, 11, 20)

    def test_deve_ordenar_por_maior_valor(self):
        self.criar_income(amount=5000)
        self.criar_expense(amount=100)

        response = self.client.get(
            "/api/transactions/all/",
            {"ordering": "↑ Price"},
        )

        results = response.data["results"]

        assert float(results[0]["amount"]) == 5000
        assert float(results[1]["amount"]) == 100

    def test_deve_ordenar_por_menor_valor(self):
        self.criar_income(amount=5000)
        self.criar_expense(amount=100)

        response = self.client.get(
            "/api/transactions/all/",
            {"ordering": "↓ Price"},
        )

        results = response.data["results"]

        assert float(results[0]["amount"]) == 100
        assert float(results[1]["amount"]) == 5000


    def test_deve_retornar_apenas_dez_transacoes_por_pagina(self):
        for i in range(12):
            self.criar_expense(
                amount=100 + i,
                expense_date=date(2026, 11, 10),
                store=f"Loja {i}",
            )

        response = self.client.get(
            "/api/transactions/all/"
        )

        assert response.status_code == 200
        assert response.data["count"] == 12
        assert len(response.data["results"]) == 10
        assert response.data["next"] is not None

    def test_deve_retornar_segunda_pagina(self):
        for i in range(12):
            self.criar_expense(
                amount=100 + i,
                expense_date=date(2026, 11, 10),
                store=f"Loja {i}",
            )

        response = self.client.get(
            "/api/transactions/all/?page=2"
        )

        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        assert response.data["previous"] is not None


    def test_nao_deve_retornar_transacoes_de_outro_usuario(self):
        outro_usuario = User.objects.create_user(
            username="OutroUsuario",
            email="outro.usuario@example.com",
            password="teste12345",
        )

        outra_conta = Account.objects.create(
            user=outro_usuario,
            name="Outra conta",
            type="Banco",
            balance=1000,
        )

        self.criar_income()
        self.criar_expense()

        Income.objects.create(
            user=outro_usuario,
            account=outra_conta,
            origin="Receita de outro usuário",
            type="Fixed",
            category="Salary",
            amount=5000,
            date=date(2026, 11, 10),
        )

        response = self.client.get(
            "/api/transactions/all/"
        )

        assert response.status_code == 200
        assert response.data["count"] == 2

        descriptions = [
            transaction["description"]
            for transaction in response.data["results"]
        ]

        assert "Receita de outro usuário" not in descriptions

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/transactions/all/"
        )

        assert response.status_code in [401, 403]

@pytest.mark.django_db
class TestGetExpenseFiltered:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)


        self.account = Account.objects.create(
            user=self.user,
            name="Banco do Brasil",
            type="Banco",
            balance=10000,
        )

        self.client.force_authenticate(user=self.user)

    def criar_expense(
        self,
        amount,
        expense_date,
        user=None,
        deleted_at=None,
    ):
        user = user or self.user

        account = self.account

        if user != self.user:
            account = Account.objects.create(
                user=user,
                name="Outra conta",
                type="Banco",
                balance=1000,
            )

        return Expense.objects.create(
            user=user,
            account=account,
            store="Supermercado",
            type="Variable",
            category="Food",
            amount=amount,
            date=expense_date,
            deleted_at=deleted_at,
        )

    def test_deve_retornar_expense_filtered(self):
        response = self.client.get("/api/transactions/expense_filtered/")
        assert response.status_code == 200
        assert "total_expense" in response.data
        assert "counted" in response.data


    def test_deve_retornar_total_e_quantidade_de_expenses(self):
        self.criar_expense(3000, date(2026, 11, 5))
        self.criar_expense(2000, date(2026, 11, 10))
        self.criar_expense(1500, date(2026, 11, 15))

        response = self.client.get(
            "/api/transactions/expense_filtered/"
        )

        assert response.status_code == 200
        assert float(response.data["total_expense"]) == 6500
        assert response.data["counted"] == 3

    def test_deve_filtrar_expenses_por_periodo(self):
        self.criar_expense(3000, date(2026, 11, 5))
        self.criar_expense(2000, date(2026, 11, 10))
        self.criar_expense(1500, date(2026, 10, 15))

        response = self.client.get(
            "/api/transactions/expense_filtered/",
            {"periods": "November 2026"},
        )

        assert response.status_code == 200
        assert float(response.data["total_expense"]) == 5000
        assert response.data["counted"] == 2


    def test_deve_filtrar_varios_periodos(self):
        self.criar_expense(3000, date(2026, 11, 5))
        self.criar_expense(2000, date(2026, 10, 10))
        self.criar_expense(1500, date(2026, 9, 15))
        self.criar_expense(1000, date(2026, 8, 20))

        response = self.client.get(
            "/api/transactions/expense_filtered/",
            {"periods": "November 2026,October 2026"},
        )

        assert response.status_code == 200
        assert float(response.data["total_expense"]) == 5000
        assert response.data["counted"] == 2


    def test_nao_deve_permitir_acesso_sem_autentificacao(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/transactions/expense_filtered/")

        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestGetIncomeFiltered:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)


        self.account = Account.objects.create(
            user=self.user,
            name="Banco do Brasil",
            type="Banco",
            balance=10000,
        )

        self.client.force_authenticate(user=self.user)

    def criar_income(
        self,
        amount,
        income_date,
        user=None,
        deleted_at=None,
    ):
        user = user or self.user

        account = self.account

        if user != self.user:
            account = Account.objects.create(
                user=user,
                name="Outra conta",
                type="Banco",
                balance=1000,
            )

        return Income.objects.create(
            user=user,
            account=account,
            origin="Empresa",
            type="Fixed",
            category="Salary",
            amount=amount,
            date=income_date,
            deleted_at=deleted_at,
        )

    def test_deve_retornar_income_filtered(self):
        response = self.client.get("/api/transactions/income_filtered/")
        assert response.status_code == 200
        assert "total_income" in response.data
        assert "counted" in response.data


    def test_deve_retornar_total_e_quantidade_de_incomes(self):
        self.criar_income(3000, date(2026, 11, 5))
        self.criar_income(2000, date(2026, 11, 10))
        self.criar_income(1500, date(2026, 11, 15))

        response = self.client.get(
            "/api/transactions/income_filtered/"
        )

        assert response.status_code == 200
        assert float(response.data["total_income"]) == 6500
        assert response.data["counted"] == 3

    def test_deve_filtrar_incomes_por_periodo(self):
        self.criar_income(3000, date(2026, 11, 5))
        self.criar_income(2000, date(2026, 11, 10))
        self.criar_income(1500, date(2026, 10, 15))

        response = self.client.get(
            "/api/transactions/income_filtered/",
            {"periods": "November 2026"},
        )

        assert response.status_code == 200
        assert float(response.data["total_income"]) == 5000
        assert response.data["counted"] == 2


    def test_deve_filtrar_varios_periodos(self):
        self.criar_income(3000, date(2026, 11, 5))
        self.criar_income(2000, date(2026, 10, 10))
        self.criar_income(1500, date(2026, 9, 15))
        self.criar_income(1000, date(2026, 8, 20))

        response = self.client.get(
            "/api/transactions/income_filtered/",
            {"periods": "November 2026,October 2026"},
        )

        assert response.status_code == 200
        assert float(response.data["total_income"]) == 5000
        assert response.data["counted"] == 2


    def test_nao_deve_permitir_acesso_sem_autentificacao(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/transactions/income_filtered/")

        assert response.status_code in [401, 403]



@pytest.mark.django_db
class TestGetAccountList:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_accounts_list(self):
          response = self.client.get("/api/transactions/accounts_list/")

          assert response.status_code == 200
          assert "accounts_list" in response.data

    def test_deve_retornar_accounts_list_corret(self):
        Account.objects.create(
            user=self.user,
            name="Banco do Brasil",
            type="Banco",
            balance=Decimal("10000.00"),
        )
        Account.objects.create(
            user=self.user,
            name="Caixa",
            type="Banco",
            balance=Decimal("5000.00"),
        )

        response = self.client.get("/api/transactions/accounts_list/")
        assert response.status_code == 200
        assert response.data["accounts_list"] == ["Banco do Brasil","Caixa"]

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/transactions/accounts_list/")

        assert response.status_code in [401, 403]

@pytest.mark.django_db
class TestGetLastFiveMonths:

    def setup_method(self):
        self.client = APIClient()
    
        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
            first_name="Teste",
            last_name="Tester"
        )
        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_last_five_months(self):
        response = self.client.get(
            "/api/transactions/last_five_months/"
        )

        assert response.status_code == 200
        assert "last_five_months" in response.data
        assert len(response.data["last_five_months"]) == 5        


    def test_deve_retornar_last_five_months_correto(self, monkeypatch):
        # Simula novembro de 2026
        monkeypatch.setattr(
            "finance.views.transactions_views.timezone.localdate",
            lambda: date(2026, 11, 25)
        )

        response = self.client.get(
            "/api/transactions/last_five_months/"
        )

        assert response.status_code == 200

        assert response.data["last_five_months"] == [
            "November 2026",
            "October 2026",
            "September 2026",
            "August 2026",
            "July 2026",
        ]

    def test_deve_funcionar_na_virada_do_ano(self, monkeypatch):
        # Simula janeiro de 2027
        monkeypatch.setattr(
            "finance.views.transactions_views.timezone.localdate",
            lambda: date(2027, 1, 15)
        )

        response = self.client.get(
            "/api/transactions/last_five_months/"
        )

        assert response.status_code == 200
        assert response.data["last_five_months"] == [
            "January 2027",
            "December 2026",
            "November 2026",
            "October 2026",
            "September 2026",
        ]

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/transactions/last_five_months/"
        )
        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestGetAllCategories:

    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="Testes",
            password="teste12345",
        )

        self.client.force_authenticate(user=self.user)

    def test_deve_retornar_all_categories(self):
        response = self.client.get(
            "/api/transactions/all_categories/"
        )

        assert response.status_code == 200
        assert "categories_list" in response.data

    def test_deve_retornar_all_categories_correto(self):

        account = Account.objects.create(
        user=self.user,
        name="Banco do Brasil",
        type="Banco",
        balance=10000,
    )

        Expense.objects.create(
            account=account,
            user=self.user,
            store="Restaurante",
            name="Almoço",
            category="Food",
            type="Variable",
            amount=100,
            date="2026-11-10",
        )

        Expense.objects.create(
            account=account,
            user=self.user,
            store="Posto",
            name="Gasolina",
            category="Transport",
            type="Variable",
            amount=200,
            date="2026-11-11",
        )

        response = self.client.get(
            "/api/transactions/all_categories/"
        )

        assert response.status_code == 200

        assert sorted(response.data["categories_list"]) == [
            "Food",
            "Transport",
        ]

    def test_nao_deve_permitir_acesso_sem_autenticacao(self):

        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/transactions/all_categories/"
        )

        assert response.status_code in [401, 403]

