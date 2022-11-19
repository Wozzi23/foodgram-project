from .settings import *

# Данный файл для модуля Pytest не удаляй если тесты пройти хочешь...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
