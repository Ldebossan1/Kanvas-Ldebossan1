from rest_framework.generics import CreateAPIView
from accounts.models import Account
from accounts.serializers import AccountSerializer


class AccountView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
