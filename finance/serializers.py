#Serializer: converte objetos Python em JSON e valida os dados recebidos.
from rest_framework import serializers
from .models import Expense, Income, Account, Goal, User


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "account",
            "store",
            "name",
            "category",
            "type",
            "date",
            "amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_account(self, account):
        request = self.context["request"]

        if account.user_id != request.user.id:
            raise serializers.ValidationError(
                "A conta selecionada não pertence ao usuário."
            )

        if account.deleted_at is not None:
            raise serializers.ValidationError(
                "Não é possível usar uma conta excluída."
            )

        return account


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = [
            "id",
            "account",
            "origin",
            "type",
            "category",
            "amount",
            "date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_account(self, account):
        request = self.context["request"]

        if account.user_id != request.user.id:
            raise serializers.ValidationError(
                "A conta selecionada não pertence ao usuário."
            )

        if account.deleted_at is not None:
            raise serializers.ValidationError(
                "Não é possível usar uma conta excluída."
            )

        return account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "type",
            "balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = [
            "id",
            "name",
            "saved",
            "objective",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
