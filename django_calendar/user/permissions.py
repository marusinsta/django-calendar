from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedWithoutCreate(IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        return super().has_permission(request, view)
