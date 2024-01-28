from rest_framework.permissions import BasePermission


class HasCalendarAccess(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.users.all()


class HasEventAccess(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.calendar.users.all()
