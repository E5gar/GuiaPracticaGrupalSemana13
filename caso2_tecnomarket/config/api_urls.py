from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='token'),
    path('', include(router.urls)),
]
