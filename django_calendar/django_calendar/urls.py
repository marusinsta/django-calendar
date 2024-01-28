from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter

from core.views import CalendarViewSet, CalendarUserManager, EventViewSet
from user.views import CustomUserViewSet, LogOutView

router = SimpleRouter()
router.register(r'api/users', CustomUserViewSet, basename='users')
router.register(r'api/calendars', CalendarViewSet, basename='calendars')
router.register(r'api/events', EventViewSet, basename='events')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', obtain_auth_token, name='api-login'),
    path('api/logout/', LogOutView.as_view(), name='api-logout'),
    path('api/calendars/<int:pk>/add_users/', CalendarUserManager.as_view(), name='add-users'),
    path('api/calendars/<int:pk>/remove_users/', CalendarUserManager.as_view(), name='remove-users'),
]

urlpatterns += router.urls
