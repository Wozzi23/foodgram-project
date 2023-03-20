from api import views

from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    'users',
    views.BaseUserViewSet,
    basename='users'
)
router.register(
    'ingredients',
    views.IngredientsViewSet,
    basename='ingredients'
)
router.register(
    'tags',
    views.TagsViewSet,
    basename='tags'
)
router.register(
    'recipes',
    views.RecipesViewSet,
    basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
