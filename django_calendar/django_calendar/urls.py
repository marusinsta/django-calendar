from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import CalendarViewSet, CalendarUserManager, EventViewSet
from user.views import CustomUserViewSet, LogOutView

router = SimpleRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'calendars', CalendarViewSet, basename='calendars')
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', obtain_auth_token, name='api-login'),
    path('api/logout/', LogOutView.as_view(), name='api-logout'),
    path('api/calendars/<int:pk>/add_users/', CalendarUserManager.as_view(), name='add-users'),
    path('api/calendars/<int:pk>/remove_users/', CalendarUserManager.as_view(), name='remove-users'),
    path('api/schema', SpectacularAPIView.as_view(), name="api-schema"),
    path('api/schema/docs', SpectacularSwaggerView.as_view(url_name="api-schema")),
]
