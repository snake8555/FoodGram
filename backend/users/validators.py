import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """Проверка username"""
    pattern = re.compile(r'^[\w.@+-]+')
    if pattern.fullmatch(value) is None:
        match = re.split(pattern, value)
        symbol = ''.join(match)
        raise ValidationError(f'Некорректные символы в username: {symbol}')
    if value == 'me':
        raise ValidationError('me нельзя использовать как имя пользователя')
