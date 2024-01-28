from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import CustomUser
from .permissions import IsAuthenticatedWithoutCreate
from .serializers import CustomUserSerializer, CustomUserShortSerializer


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedWithoutCreate,)

    def get_serializer_class(self):
        if self.action == "list":
            return CustomUserShortSerializer
        return CustomUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"token": Token.objects.get(user=CustomUser.objects.get(id=serializer.data['id'])).key},
                        status=status.HTTP_201_CREATED, headers=headers)


class LogOutView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            return Response({"message": "Failed to logout"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"success": "Successfully logged out"}, status=status.HTTP_200_OK)
