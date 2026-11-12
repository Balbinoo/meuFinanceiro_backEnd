from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import User
from ..serializers import UserSerializer, RegisterSerializer

from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            pk=self.request.user.pk,
            deleted_at__isnull=True,
        )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
