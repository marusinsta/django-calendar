from django.urls import resolve, reverse
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user.models import CustomUser
from .models import Calendar, Event
from .serializers import CalendarSerializer, EventSerializer, CalendarEmptySerializer
from .permissions import HasCalendarAccess, HasEventAccess


class CalendarViewSet(ModelViewSet):
    serializer_class = CalendarSerializer
    queryset = Calendar.objects.all()
    permission_classes = (IsAuthenticated & HasCalendarAccess,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(users=user)

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user
        if 'users' not in request.data:
            request.data['users'] = [request.user.username]
        else:
            request.data['users'].append(request.user.username)
        return super(ModelViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if 'users' in request.data:
            pk = self.kwargs['pk']
            add_users_url = reverse('add-users', kwargs={'pk': str(pk)})
            remove_users_url = reverse('remove-users', kwargs={'pk': str(pk)})
            return Response({"message": f"Use {add_users_url} to add or {remove_users_url} to remove users."},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'owner' in request.data:
            pk = self.kwargs['pk']
            calendar = Calendar.objects.get(pk=pk)
            is_present = False
            new_owner_name = request.data['owner']
            for user in calendar.users.all():
                if user.username == new_owner_name:
                    is_present = True
                    break
            if not is_present:
                return Response({"message": f"User '{request.data['owner']}' does not have access to this calendar"},
                                status=status.HTTP_400_BAD_REQUEST)
        return super(ModelViewSet, self).update(request, *args, **kwargs)


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = (IsAuthenticated & HasEventAccess,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        user_calendars = Calendar.objects.filter(users=user)
        return self.queryset.filter(calendar__in=user_calendars)

    def create(self, request, *args, **kwargs):
        calendar_status = self._check_if_calendar_is_valid(request)
        if calendar_status == status.HTTP_200_OK:
            return super(ModelViewSet, self).create(request, *args, **kwargs)
        else:
            return Response(status=calendar_status)

    def update(self, request, *args, **kwargs):
        calendar_status = self._check_if_calendar_is_valid(request)
        if calendar_status == status.HTTP_200_OK:
            return super(ModelViewSet, self).update(request, *args, **kwargs)
        else:
            return Response(status=calendar_status)

    def _check_if_calendar_is_valid(self, request):
        if 'calendar' in request.data:
            calendar_id = request.data['calendar']
            try:
                calendar = Calendar.objects.get(pk=calendar_id)
            except Exception:
                return status.HTTP_400_BAD_REQUEST
            if request.user not in calendar.users.all() and not request.user.is_staff:
                return status.HTTP_403_FORBIDDEN
        return status.HTTP_200_OK


class CalendarUserManager(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CalendarSerializer

    @extend_schema(responses={
        "200": OpenApiResponse(response=CalendarSerializer, description="Successfully updated users"),
        "4XX": OpenApiResponse(response=CalendarEmptySerializer, description="Failed to update users")
    })
    def post(self, request, pk):
        try:
            calendar = Calendar.objects.get(id=pk)
        except Exception:
            return Response({"message": f"Calendar with id '{pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)
        if request.user not in calendar.users.all() and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        users = []
        for new_user in request.data['users']:
            try:
                users.append(CustomUser.objects.get(username=new_user))
            except Exception:
                return Response({"message": f"User with username '{new_user}' does not exist."},
                                status=status.HTTP_404_NOT_FOUND)
        view_name = resolve(request.path).view_name
        if view_name == "add-users":
            for user in users:
                calendar.users.add(user)
        if view_name == "remove-users":
            for user in users:
                if user.id == calendar.owner.id:
                    return Response({"message": "Can't remove owner."}, status=status.HTTP_400_BAD_REQUEST)
                if user not in calendar.users.all():
                    return Response({"message": f"User '{user}' does not have access to this calendar."},
                                    status=status.HTTP_400_BAD_REQUEST)
            for user in users:
                calendar.users.remove(user)
        return Response(data=CalendarSerializer(calendar).data, status=status.HTTP_200_OK)
