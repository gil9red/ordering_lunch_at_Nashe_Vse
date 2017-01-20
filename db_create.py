#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


# # TODO: оформить
# """
# https://habrahabr.ru/post/196810/
#
# Создание базы данных
#
# Мы покончили с конфигурацией и моделью, теперь мы готовы создать файл с нашей базой данных. Пакет SQLAlchemy-migrate поставляется с инструментами командной строки и API для создания баз данных, которые позволят легко обновляться в будущем, что мы и будем делать. Я нахожу инструменты командной строки местами неудобными в использовании, поэтому вместо них я написал свой набор маленьких Python скриптов, которые вызывают API миграций.
#
# Отмечу, что скрипт полностью универсален. Все специфические пути импортированы из конфигурационного файла. Когда вы начнете свой собственный проект, то можете просто копировать скрипт в папку нового приложения, и он сразу будет рабочим.
#
# Чтобы создать базу данных, вам нужно просто запустить скрипт (помните, что если вы на Windows, то команда слегка отличается):
#
# ./db_create.py
#
#
#
# После ввода команды вы получите новый файл app.db. Это пустая база данных sqlite, изначально поддерживающая миграции. У вас также есть директория db_repository с несколькими файлами внутри. В этом месте SQLAlchemy-migrate хранит свои файлы с данными. Замечу, что не пересоздаем репозиторий, если он уже создан. Это позволит нам воссоздать базы данных из существующего репозитория, если понадобится.
# """


# При импорте db из models также будут добавлены класс-таблицы базы
from models import db

# db.drop_all()
db.create_all()

# TODO: не нравится migrate, попробую перейти на alembic
# https://bitbucket.org/zzzeek/alembic
# http://alembic.readthedocs.io/en/latest/cookbook.html
# https://pypi.python.org/pypi/Flask-Alembic
# https://flask-script.readthedocs.io/en/latest/
#
# https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/


# from config import SQLALCHEMY_DATABASE_URI
# from config import SQLALCHEMY_MIGRATE_REPO
#
# from migrate.versioning import api
# import os.path
#
# if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
#     api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
#     api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# else:
#     api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
