#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


"""
Меню находится в определенных письмах, приложенное как docx-файл.
Скрипт считывает последнее письмо, вытаскивает и сохраняет приложенный файл и
считывает из него таблицы меню и отображает таблицы на веб странице.

Устанавливать docx так: pip install python-docx

"""


# NOTE: костыль для винды, для исправления проблем с исключениями
# при выводе юникодных символов в консоль винды
import sys
if sys.platform == 'win32':
    import codecs
    # Для винды кодировкой консоли будет cp866
    sys.stdout = codecs.getwriter(sys.stdout.encoding)(sys.stdout.detach(), 'backslashreplace')
    sys.stderr = codecs.getwriter(sys.stderr.encoding)(sys.stderr.detach(), 'backslashreplace')


import traceback
import os

import config

from app import app
import api

import logging

from flask import render_template, request


if config.debug_without_email:
    from app import session
    from models import LunchInfo, UserOrderLunch, Lunch, db
    from datetime import datetime

    db.create_all()

    lunch_id = 9999
    session.add(LunchInfo(id=0, lunch_id=lunch_id, subject="Тестовое Меню бизнес-ланча", date=datetime.today()))

    i = 0

    def add_lunch(name, weight, price, category):
        global i
        i += 1
        session.add(Lunch(id=i, lunch_id=lunch_id, name=name, weight=weight, price=price, category=category))

    add_lunch(name="Салат 'Цезарь'", weight='100 гр', price='100 руб.', category='Салаты')
    add_lunch(name="Салат 'Под шубой'", weight='100 гр', price='100 руб.', category='Салаты')
    add_lunch(name="Пельмешки", weight='110 гр', price='60 руб.', category='Горячее')
    add_lunch(name="Борщ", weight='150 мл', price='65 руб.', category='Супа')
    add_lunch(name="Окрошка", weight='150 мл', price='65 руб.', category='Супа')
    add_lunch(name="Чай", weight='250 мл', price='40 руб.', category='Напитки')
    add_lunch(name="Кофе", weight='100 мл', price='70 руб.', category='Напитки')
    add_lunch(name="Пиво", weight='200 мл', price='80 руб.', category='Напитки')
    add_lunch(name="Печеньки", weight='100 гр', price='50 руб.', category='Десерты')

    session.add(UserOrderLunch(user_ip='1', order='1,2', additionally='Хлеба', lunch_id=lunch_id))
    session.add(UserOrderLunch(user_ip='2', order='3,4', lunch_id=lunch_id))

    session.commit()


# TODO: можно перенести его в класс пользователя
def is_admin():
    """Функция возвращает True, если адрес запросов -- от админа."""

    from flask import request
    user_ip = request.remote_addr

    return user_ip in config.ip_admins


# TODO: блюда с запятыми в название нужно как то выделять -- это могут быть наборы/варианты
# блюда и нужно тогда указать конкретное
# TODO: Меню получено <вчера/сегодня и т.п.>. При наведении или клике можно и дату показать
@app.route("/", methods=['GET', 'POST'])
def index():
    try:
        user_ip = request.remote_addr
        logging.debug('%s: %s from %s.', request.path, request.method, user_ip)

        last_lunch_id = api.save_last_lunch_menu()
        logging.debug('last_lunch_id: %s.', last_lunch_id)

        # Запрос для получения информации заказа меню определенного пользователя
        # или создания, если ее для текущего пользователя/меню нет
        selected_id_menu = None
        additionally_text = None

        if request.method == 'POST':
            additionally_text = request.form['additionally_text']
            logging.debug('additionally_text: %s.', additionally_text)

            # Конвертация в число и сортировка по порядку
            selected_id_menu = sorted([int(v) for k, v in request.form.items() if k.startswith('select_')])
            logging.debug('Selected_id_menu: %s.', selected_id_menu)

        user_lunch = api.get_or_create_new_user_order_lunch(user_ip, last_lunch_id,
                                                            selected_id_menu, additionally_text)
        logging.debug('User: %s.', user_lunch)

        lunch_info = api.get_lunch_info(last_lunch_id)
        subject = lunch_info.subject
        date = lunch_info.date.strftime(config.header_date_format)
        logging.debug('subject: %s.', subject)
        logging.debug('date: %s.', date)

        rows = api.get_row_lunchs_menu_for_html_render(last_lunch_id, user_lunch)
        logging.debug('rows: %s.', rows)

        selected_rows = [row for row in rows if row['is_item'] and row['is_selected']]
        logging.debug('selected_rows: %s.', selected_rows)
        logging.debug('selected_lunchs: %s.', [row['name'] for row in selected_rows])

        total_weights, total_prices = api.get_total_price_and_weight(selected_rows)
        logging.debug('total_weights: %s.', total_weights)
        logging.debug('total_prices:  %s.', total_prices)

    except ImportError:
        logging.error(traceback.format_exc())
        quit()

    except BaseException as e:
        # TODO: use debug flask
        logging.error(e)
        logging.error(traceback.format_exc())
        return 'Error: "{}".'.format(e), 500

    # TODO: привести к одному виду форматирование стилей строки (например: class="total")
    # TODO: использовать wtforms для создания вебморды: http://wtforms.readthedocs.io/en/latest/widgets.html
    return render_template(
        "index.html",
        rows=rows, subject=subject, date=date,
        selected_rows=selected_rows,
        total_weights=total_weights,
        total_prices=total_prices,
        column_count=3,
        is_admin=is_admin(),

        user=user_lunch,

        need_to_show_message_on_ready=False,
        message=r"!!!\n\nhghjgjhgjh",
    )


@app.route("/link")
def link():
    file_name = 'Меню бизнес-ланча.url'
    static_file_name = os.path.join('static', file_name)

    api.create_url_file(static_file_name)

    # Перенаправляем к url с файлом
    from flask import render_template_string, redirect
    relative_url = render_template_string("{{ url_for('static', filename='%s') }}" % (file_name, ))
    return redirect(relative_url)


# TODO: каждую "строку" в заказе разрисовать одним цветом, чтобы визуально можно было
# отличить заказы пользователей: style="background-color: rgba(0, 0, 0, 0.5);"
# TODO: Про flask https://habrahabr.ru/post/251415/
# TODO: помнить галочки на странице админа
# TODO: опциональное удаление в названии блюд строку в скобках -- в них похоже
# всегда описываются ингридиенты
# TODO: проверка новых данных:
# https://webcache.googleusercontent.com/search?q=cache:LopagNIhaeQJ:https://nulled.cc/threads/113073/+&cd=6&hl=ru&ct=clnk&gl=ru&client=firefox-b-ab
@app.route("/admin", methods=['GET', 'POST'])
# TODO: decline
# @app.route("/admin/<user_online_date>")
# @app.route("/admin/<start_user_online_date>-<last_user_online_date>")
def admin(user_online_date=None, start_user_online_date=None, last_user_online_date=None):
    user_ip = request.remote_addr
    logging.debug('%s: %s from %s.', request.path, request.method, user_ip)
    logging.debug('user_online_date: %s, start_user_online_date: %s, last_user_online_date: %s.',
                  user_online_date, start_user_online_date, last_user_online_date)

    # Проверяем что ip не админа
    if not is_admin():
        from flask import abort
        abort(404)

    need_to_show_message_on_ready = request.method == 'POST'
    message = 'Письмо успешно отправлено!'

    if request.method == 'POST':
        email_text = request.form['email_text']
        logging.debug('Текст заказа:\n%s', email_text)

        # TODO: в api перенести
        # TODO: вроде бы хватит и last_email_id использовать
        last_lunch_id = api.save_last_lunch_menu()
        logging.debug('last_lunch_id: %s.', last_lunch_id)

        # При создании проверяем, что такого заказа в базе нет
        # TODO: возможно, лучше показывать сообщения в глобальной позиции -- после обновления
        # кнопка может оказаться вне предело экрана и не будет видно сообщения
        try:
            from models import OrderMenu
            from app import session

            order_menu = OrderMenu(user_ip, last_lunch_id, email_text)
            session.add(order_menu)
            session.commit()

            # TODO: дело в том, что если понадобится узнать кто отправил письмо,
            # можно сразу в логах увидеть только ip, что не всегда удобно
            # TODO: вынести в апи или в модель метод получения пользователя
            from models import UserOrderLunch
            user = session.query(UserOrderLunch)\
                .filter(UserOrderLunch.lunch_id == last_lunch_id)\
                .filter(UserOrderLunch.user_ip == user_ip)\
                .one()
            user_name = user.name
            logging.debug('Заказ отправил %s (%s).', user_ip, user_name)
            logging.debug('Новый заказ меню: %s.', order_menu)

            # Если дошли до этой проверки, заказ уникальный
            if config.debug_without_email:
                logging.debug('Отправки письма не будет')
            else:
                # TODO: после отправки заказа на почту на странице вывести уведомление
                # о том, что прошло удачно
                # TODO: обработка ошибок при неудачи во время отправки письма
                from datetime import date
                subject = 'Заказ меню за {}'.format(date.today().strftime("%d/%m/%Y"))
                api.send_email(subject, email_text)

        except OrderMenu.OrderMenuAlreadyExists as e:
            logging.debug('Заказ меню уже существует: %s.', e.order_menu)

            # TODO: оформить
            message = 'Письмо уже было отправлено в {}.'.format(e.order_menu.date_time)
        # TODO: в api перенести

    # # TODO: decline
    # # можно попробовать брать только пользователей, выбравших последнее меню
    # users = api.get_today_users()
    # users = api.get_users_by_online_date(user_online_date)
    users = api.get_last_menu_users()
    logging.debug('Users: %s.', users)

    for user in users:
        logging.debug('Lunchs: %s: %s.', user.user_ip, user.get_user_lunchs_list())

    logging.debug('Exclude ip: %s.', config.ip_exclude_in_order_for_the_admin_page)
    logging.debug('Before exclude users: %s.', len(users))
    users = [user for user in users if user.user_ip not in config.ip_exclude_in_order_for_the_admin_page]
    logging.debug('After exclude users: %s.', len(users))

    # TODO: при повторной попытке отправки письма, показывать диалог с выбором действия,
    # чтобы исключить попытку случайной отправки копии (No/Cancel кнопка по умолчанию
    # TODO: показывать дату и время отправки письма в том диалоге и на странице админа,
    # а если письмо было отправлено недавно, то более человеческое, например: 10 минут
    # назад, минуту назад, 45 секунд назад и т.п.
    from flask import render_template
    return render_template(
        "admin.html",
        users=users,
        title='Пользователи за ' + ('сегодня' if user_online_date is None else user_online_date),
        user_online_date=user_online_date,
        email_header=config.email_header,
        email_footer=config.email_footer,

        # Отправитель письма с заказом
        sender=config.sender,

        # Адреса получения письма и копии письма
        to_email=config.to_email,
        to_cc_emails=config.to_cc_emails,

        need_to_show_message_on_ready=need_to_show_message_on_ready,
        message=message,
    )


# TODO: при ошибках импорта убивать сервер
if __name__ == '__main__':
    # TODO: использование logging.exception вместо ручного формирование лога
    # TODO: возможность выбрать в шт блюда (однако, как часто выбирают больше одного?)
    # TODO: более светлый цвет подвала / footer
    # TODO: настройка дебага фласка: http://flask.pocoo.org/docs/0.10/errorhandling/#working-with-debuggers
    # http://flask.pocoo.org/docs/latest/config/
    #
    # TODO: add migrate: https://habrahabr.ru/post/196810/
    # TODO: выбор чекбокса кликом по строке таблицы, содержащей чекбокс
    # TODO: перенести стили в css файл
    # TODO: link для страницы админа
    # TODO: "общее" с юзером, типа: "Господин, сегодня просто чудесный день,
    # чтобы попрбовать <рандомные блюда>"
    # Или: смотреть на блюда, выбранные ранее и предлагать их если они есть
    # в текущем меню, типа: "Госпожа, сегодня снова выберете <блюда>?"
    # TODO: сделать репозиторий публичным и выложить ссылку на него на index

    app.run(host=config.HOST, port=config.PORT)
