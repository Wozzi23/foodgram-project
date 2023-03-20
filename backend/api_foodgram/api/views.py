from api.filters import RecipesFilters
from api.paginations import CustomPageNumberPagination
from api.permissions import ReadAnyOrAuthorOnly
from api.serializers import (IngredientsSerializer, RecipeMinifiedSerializer,
                             RecipesSerializer, SetPasswordSerializer,
                             SignUpSerializer, SubscriptionsSerializer,
                             TagsSerializer)

from api_foodgram.settings import STATIC_ROOT

from django.db.models import Count
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (FavoriteRecipes, IngredientInRecipe, Ingredients,
                            Recipes, ShoppingCart, Tags)

from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.models import User


class BaseUserViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    Класс обрабатывает запросы по маршруту users

    ...

    Методы
    ------
    get_permissions():
        Устанавливает ограничения на запросы для неавторизованных пользователей
    set_password(request):
        Обрабатывает запросы по маршруту users/set_password/
    me(self, request):
        Обрабатывает запросы по маршруту users/me/
    subscriptions_list(request):
        Обрабатывает запросы по маршруту users/subscriptions/
    def subscribe(request, **kwargs):
        Обрабатывает запросы по маршруту users/{id}/subscribe/
    """

    pagination_class = CustomPageNumberPagination
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def get_permissions(self):
        """
        Устанавливает ограничения на запросы для неавторизованных пользователей

        Возвращаемое значение
        ---------------------
        bool
        """
        if self.action == 'list' or self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='set_password',
    )
    def set_password(self, request):
        """
        Обрабатывает запросы по маршруту users/set_password/

        Параметры
        ---------
        request: dict

        Возвращаемое значение
        ---------------------
        dict
        """
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def me(self, request):
        """
        Обрабатывает запросы по маршруту users/me/

        Параметры
        ---------
        request: dict

        Возвращаемое значение
        ---------------------
        dict
        """
        serializer = SignUpSerializer(
            self.request.user,
            context={'request': self.request},
            read_only=True
        )
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions_list(self, request):
        """
        Обрабатывает запросы по маршруту users/subscriptions/

        Параметры
        ---------
        request: dict

        Возвращаемое значение
        ---------------------
        dict
        """
        subscriptions = (
            User.objects.filter(
                subscribe_author__user=self.request.user).
            prefetch_related('recipes').
            annotate(recipes_count=Count('recipes')).order_by('id')
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(
            context={'request': self.request},
            data=page,
            many=True
        )
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
    )
    def subscribe(self, request, **kwargs):
        """
        Обрабатывает запросы по маршруту users/{id}/subscribe/

        Параметры
        ---------
        request: dict

        **kwargs: dict
            Дополнительные параметры переданные в запросе

        Возвращаемое значение
        ---------------------
        dict
        """
        autor_id = int(kwargs['pk'])
        user = self.request.user
        if request.method == 'POST':
            if user.id == autor_id:
                raise ValidationError(
                    {'errors': 'Нельзя подписаться на самого себя'}
                )
            author = get_object_or_404(
                User.objects.prefetch_related('recipes').
                annotate(recipes_count=Count('recipes')).
                order_by('id'),
                id=autor_id
            )
            is_subscribed = (
                user.subscribe_user.filter(author=author).exists())
            if is_subscribed:
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.subscribe_user.create(author=author)
            serializer = (
                SubscriptionsSerializer(
                    author,
                    context={'request': self.request},
                )
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        author = get_object_or_404(User, id=autor_id)
        user = self.request.user
        is_subscribed = user.subscribe_user.filter(author=author)
        if is_subscribed.exists():
            is_subscribed.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписанны на этого автора'},
            status=status.HTTP_400_BAD_REQUEST
        )


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс обработки GET запроса Ingredients
    """

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name', ]
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс обработки GET запроса Tags
    """

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


def post_delete_method(self, request, pk, model):
    """
    Базовая функция для favorite и shopping_cart

    Параметры
    ---------
        request: dict
        pk: int
        model: class

    Возвращаемое значение
    ---------------------
    dict
    """
    recipe = get_object_or_404(Recipes, id=pk)
    user = self.request.user
    if request.method == 'POST':
        favorite_recipes, create = (
            model.objects.get_or_create(
                user=user,
                recipe=recipe
            )
        )
        if create:
            return Response(
                RecipeMinifiedSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': 'Рецепт уже добален'},
            status=status.HTTP_400_BAD_REQUEST
        )
    favorite_recipes = model.objects.filter(user=user, recipe=recipe)
    if favorite_recipes.exists():
        favorite_recipes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Рецепт не был добален'},
        status=status.HTTP_400_BAD_REQUEST
    )


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Класс обработки выдачи рецептов.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (ReadAnyOrAuthorOnly,)
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipesFilters
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
        'trace'
    ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
    )
    def favorite_recipe(self, request, pk):
        """
        Функция добавления/удаления рецепта из избранного.
        """
        return post_delete_method(self, request, pk, FavoriteRecipes)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """
        Функция добавления/удаления рецепта из списка покупок.
        """
        return post_delete_method(self, request, pk, ShoppingCart)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """
        Функция выдает PDF файл со списком покупок.
        """
        ing = (
            IngredientInRecipe.objects.filter(
                recipe__shoppingcart__user=self.request.user
            )
        )
        if not ing.exists():
            raise ValidationError(
                {'errors': 'У вас нет рецептов с списке покупок'}
            )
        res = {}
        for i in ing:
            value = res.get(i.ingredient.name)
            if value is not None:
                value[1] += i.amount
            else:
                res.update(
                    {
                        i.ingredient.name:
                            [i.ingredient.measurement_unit, i.amount]
                    }
                )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="file.pdf"'

        p = canvas.Canvas(response)
        my_font_object = ttfonts.TTFont(
            'Arial', f'{STATIC_ROOT}/fonts/arial.ttf'
        )
        pdfmetrics.registerFont(my_font_object)
        p.setFont('Arial', 24)
        p.drawString(100, 700, 'Список покупок:')
        p.setFont('Arial', 14)
        x = 680
        num = 1
        for key, val in res.items():
            p.drawString(120, x, f'{num}. {key} {val[1]} {val[0]}')
            x -= 20
            num += 1
        p.showPage()
        p.save()
        return response
