from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (AmountIngredient, Cart, Favorite, Ingredient,
                            Recipe, Tag)
from users.models import Subscribe, User

from .filters import IngredientsFilter, RecipesFilterSet
from .paginations import CustomPagination
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          ShortSerializer, SubscribeSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User и Subscribe"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdminAuthorOrReadOnly]

    @action(
        methods=['get'], detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получить подписки пользователя"""
        serializer = SubscribeSerializer(
            self.paginate_queryset(
                Subscribe.objects.filter(user=request.user)
            ), many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Функция подписки и отписки."""
        user = request.user
        author = get_object_or_404(User, pk=id)
        obj = Subscribe.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if user == author:
                return Response({'errors': 'На себя подписаться нельзя'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            if obj.exists():
                return Response(
                    {'errors': f'Вы уже подписаны на {author.username}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                Subscribe.objects.create(user=user, author=author),
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if user == author:
            return Response(
                {'errors': 'Вы не можете отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Вы уже отписались от {author.username}'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Category."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = [IsAdminAuthorOrReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ingredient."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = [IngredientsFilter]
    search_fields = ('^name',)
    permission_classes = [IsAdminAuthorOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilterSet
    filter_backends = (DjangoFilterBackend, )
    add_serializer = ShortSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdminAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        else:
            return RecipePostSerializer

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial'):
            return Response(
                {'detail': 'Метод PUT не разрешен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        else:
            return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Cart, request.user, pk)
        else:
            return self.delete_from(Cart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    def create_shopping_cart(self, ingredients):
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['ingredient_value']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = AmountIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_value=Sum('amount'))
        if len(ingredients) == 0:
            return Response({'error': 'Список покупок пуст'
                             }, status=status.HTTP_400_BAD_REQUEST)
        return self.create_shopping_cart(ingredients)
