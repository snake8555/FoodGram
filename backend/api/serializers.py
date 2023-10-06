from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import Subscribe, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Получаем статус подписки на автора."""
        user = self.context.get('request').user
        return (
            user.is_authenticated and obj.follower.filter(user=user).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор регистрации юзеров."""
    email = serializers.EmailField(
        required=True, max_length=254)
    username = serializers.CharField(
        required=True, max_length=150)
    first_name = serializers.CharField(
        required=True, max_length=150)
    last_name = serializers.CharField(
        required=True, max_length=150)
    password = serializers.CharField(
        required=True, max_length=150)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


class ShortSerializer(serializers.ModelSerializer):
    """Сериализатор короткого ответа рецептов для подписок и избранного."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """Получаем статус подписки на автора."""
        return obj.user.follower.exists()

    def get_recipes(self, obj):
        """Получаем рецепты, на которые подписаны и ограничиваем по лимитам."""
        serializer = ShortSerializer(obj.author.recipe_author, many=True)
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipes = obj.author.recipe_author.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = ShortSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Считаем рецепты автора, на которого подписан пользователь."""
        return obj.author.recipe_author.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('__all__')


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор кол-ва ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор вывода рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(many=True, read_only=True,
                                             source='amountingredient_set')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'image', 'author',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorite_set.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.cart_set.filter(recipe=obj).exists()
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredients',
                                            queryset=Ingredient.objects.all())

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор записи рецептов."""
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'image', 'name', 'text',
                  'cooking_time')

    def validate_ingredients(self, data):
        if len(data) == 0:
            raise ValidationError('Список ингредиентов не может быть пустым.')
        seen_ingredinets = set()
        for ingredient in data:
            ingredient_id = ingredient['ingredients']
            if ingredient_id in seen_ingredinets:
                raise ValidationError('Ингредиенты не должны повторяться.')
            seen_ingredinets.add(ingredient_id)

            if ingredient.get('amount') < 1:
                raise ValidationError(
                    'Убедитесь, что значение ингредиента больше 0.'
                )

        return data

    def validate_cooking_time(self, data):
        if data < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть '
                'положительным целым числом и больше 0.'
            )

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            AmountIngredient(
                recipe=recipe,
                ingredients=ingredient_data['ingredients'],
                amount=ingredient_data['amount']
            ).save()

        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe.amountingredient_set.all().delete()
        for ingredient_data in ingredients_data:
            AmountIngredient(
                recipe=recipe,
                ingredients=ingredient_data['ingredients'],
                amount=ingredient_data['amount']
            ).save()

        recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def delete(self, recipe):
        recipe.delete()

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data
