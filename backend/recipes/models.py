from colorfield.fields import ColorField
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(verbose_name='название', max_length=16,
                            unique=True)
    color = ColorField(verbose_name='цвет', format='hex', max_length=32,
                       unique=True)
    slug = models.SlugField(verbose_name='slug', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(verbose_name='название', max_length=128)
    measurement_unit = models.CharField(verbose_name='единица измерения',
                                        max_length=16)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField(verbose_name='название рецепта', max_length=200,
                            unique=True)
    text = models.TextField(verbose_name='описание',)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipe_author',
                               verbose_name='автор')
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='время приготовления (мин)'
    )
    tags = models.ManyToManyField(Tag, verbose_name='теги')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='AmountIngredient',
                                         verbose_name='ингредиенты')
    image = models.ImageField(verbose_name='изображение', upload_to='recipes/')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    """Связующая модель кол-ва ингредиентов в рецепте."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='рецепт')
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.CASCADE,
                                    verbose_name='ингредиент')
    amount = models.PositiveSmallIntegerField(default=0,
                                              verbose_name='количество')

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredients'],
                name='ingredienttorecipe_unique'
            )
        ]


class UserRecipe(models.Model):
    """Абстрактная модель для избранного и списка покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='рецепт')

    class Meta:
        abstract = True
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'Пользователь:{self.user.username}, рецепт: {self.recipe.name}'


class Favorite(UserRecipe):
    """Модель избранного."""

    class Meta(UserRecipe.Meta):
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class Cart(UserRecipe):
    """Модель списка покупок."""

    class Meta(UserRecipe.Meta):
        default_related_name = 'cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в список покупок'
