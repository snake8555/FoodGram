import csv
import datetime

from django.core.management import BaseCommand

from recipes.models import Ingredient

csv_files = [
    (Ingredient, 'ingredients.csv')
]

fields = (
    ('name', 'measurement_unit')
)


class Command(BaseCommand):
    help = ('Загрузка data из data/*.csv.'
            'Запуск: python manage.py load_csv_data.')

    def handle(self, *args, **options):
        print('Старт импорта')
        start_time = datetime.datetime.now()

        try:
            for model, file in csv_files:
                with open(
                        f'recipes/management/data/{file}', encoding='utf-8'
                ) as f:
                    reader = csv.reader(f, delimiter=',')
                    for row in reader:
                        if model == Ingredient:
                            row_data = {
                                'name': row[0],
                                'measurement_unit': row[1]
                            }
                        obj, created = model.objects.get_or_create(**row_data)
                        if created:
                            print(f'{obj} загружен в таблицу {model.__name__}')
                        else:
                            print(
                                f'{obj} уже загружен в таблицу '
                                f'{model.__name__}')

            print(f'Загрузка данных завершена за'
                  f' {(datetime.datetime.now() - start_time).total_seconds()} '
                  f'сек.')

        except Exception as error:
            print(f'Сбой в работе импорта: {error}.')

        finally:
            print('Завершена работа импорта.')
