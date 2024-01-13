from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter

from core.views import CalendarViewSet, CalendarUserManager
from user.views import CustomUserViewSet

router = SimpleRouter()
router.register(r'user', CustomUserViewSet)
router.register(r'calendar', CalendarViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('api/calendar/<int:pk>/add_users/', CalendarUserManager.as_view(), name='add-user'),
]

urlpatterns += router.urls
