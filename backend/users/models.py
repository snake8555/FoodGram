from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель User."""
    username = models.CharField('Имя пользователя (никнейм)',
                                validators=[validate_username],
                                max_length=150, unique=True)
    email = models.EmailField('Почта', max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150)

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='cant subscribe to yourself',
            ),
        ]

    def __str__(self):
        return (
            f'Подписчик: {self.user.username}, Автор: {self.author.username}'
        )
