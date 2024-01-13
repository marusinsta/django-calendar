from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user.models import CustomUser
from user.permissions import IsAuthenticatedWithoutCreate
from .models import Calendar
from .serializers import CalendarSerializer


class CalendarViewSet(ModelViewSet):
    serializer_class = CalendarSerializer
    queryset = Calendar.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(users=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if 'users' not in serializer.initial_data:
            serializer.initial_data['users'] = [request.user.username]
        else:
            serializer.initial_data['users'].append(request.user.username)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CalendarUserManager(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            calendar = Calendar.objects.get(id=pk)
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user not in calendar.users.all() and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        users = []
        for new_user in request.data['users']:
            try:
                users.append(CustomUser.objects.get(username=new_user))
            except Exception as e:
                return Response({"message": f"User with username '{new_user}' does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)
        for user in users:
            calendar.users.add(user)
        return Response(status=status.HTTP_200_OK)
