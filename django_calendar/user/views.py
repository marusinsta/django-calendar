from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import CustomUser
from .permissions import IsAuthenticatedWithoutCreate
from .serializers import CustomUserSerializer


class CustomUserViewSet(ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedWithoutCreate,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"token": Token.objects.get(user=CustomUser.objects.get(id=serializer.data['id'])).key},
                        status=status.HTTP_201_CREATED, headers=headers)
