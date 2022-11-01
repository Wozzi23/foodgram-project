from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('users', views.BaseUserViewSet, basename='users')
router.register('ingredients', views.IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
