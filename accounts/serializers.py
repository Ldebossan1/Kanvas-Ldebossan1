from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "username",
            "password",
            "email",
            "is_superuser",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "username": {
                "validators": [
                    UniqueValidator(
                        queryset=Account.objects.all(),
                        message="A user with that username already exists.",
                    )
                ]
            },
            "email": {
                "validators": [
                    UniqueValidator(
                        queryset=Account.objects.all(),
                        message="user with this email already exists.",
                    )
                ]
            },
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        is_superuser = validated_data["is_superuser"]

        if is_superuser:
            return Account.objects.create_superuser(**validated_data)

        return Account.objects.create_user(**validated_data)
