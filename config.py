#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


version = '1.0.0'

# Например: <username>@mail.com
username = "<username>"
password = "<password>"

# email отправителя, т.е. наша почта
sender = 'username@mail.com>'

# Например: smtp.mail.ru
smtp_server = "<smtp_server>"

# email отправителя писем с прикрепленными файлами обеденных меню в docx
lunch_email = "<lunch_email>"

# email, на который нужно отправить письма с заказом меню
to_email = "to_email"

# Получатели копии письма
to_cc_emails = []

header_date_format = "%d/%m/%Y %H:%M:%S"

debug = True
# debug = False

debug_bd = False

# Указывает нужно ли выводить сообщения общения smtp сервера и
# нашего скрипта при отправке писем
debug_smtp = True

# Тестовый режим работы без проверки меню в письмах и использовании базы в памяти
debug_without_email = False

config_file_name = 'log.txt'

# TODO: лучше, конечно, в базе хранить как роли
# Список админов
ip_admins = [
    'localhost', '127.0.0.1',
]

# TODO: нормальное название, покороче
# Исключить ip в заказе на странице админа
ip_exclude_in_order_for_the_admin_page = [
    'localhost',
    '127.0.0.1',
]

# Заголовок и подвал отправляемого письма с заказом
email_header = r"Здравствуйте!\nЗаказ на 12:40\n\n"
email_footer = r"Спасибо!"


# TODO: настройка конфига https://habrahabr.ru/post/251415/

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SQLALCHEMY_ECHO = debug_bd
SQLALCHEMY_TRACK_MODIFICATIONS = True


if debug_without_email:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Public IP
HOST = '0.0.0.0'

# Local IP
HOST = 'localhost'

PORT = 5000


# TODO: при реализации конфигов сделать настройкой конфига
# При запуске сервера в локалхосте показывать его в заказах
if HOST == 'localhost':
    ip_exclude_in_order_for_the_admin_page.remove('localhost')
    ip_exclude_in_order_for_the_admin_page.remove('127.0.0.1')
