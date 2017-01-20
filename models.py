#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from app import db


class UserOrderLunch(db.Model):
    """
    Класс описывает таблицу заказа пользователя.

    """

    __tablename__ = 'UserOrdersLunch'

    # IP пользователя
    user_ip = db.Column(db.String, primary_key=True)

    name = db.Column(db.String)

    # Заказ пользователя
    order = db.Column(db.String, default='')

    # Дополнительные пожелания (хлеб, в контейнере, и т.п.)
    additionally = db.Column(db.String, default='')

    # Уникальный номер меню. Соответствует id письма, из которого было получено.
    # lunch_id = db.Column(db.Integer)
    lunch_id = db.Column(db.Integer, primary_key=True)

    # Дата и время последнего обращение к странице с заказами
    last_online_date = db.Column(db.DateTime)

    # Дата и время последнего выбора блюд меню
    last_select_lunch_date = db.Column(db.DateTime)

    def get_lunch_id_list(self):
        return sorted([int(_) for _ in self.order.split(',')]) if self.order else list()

    def get_user_lunchs_list(self):
        """
        Функция возвращает список выбранных пользователем блюд (объекты Lunch),
        относящихся к определенному меню (lunch_id).

        """

        import api
        lunchs = api.get_lunchs_list(self.lunch_id)

        # Получим id заказанных блюд
        lunch_id_list = self.get_lunch_id_list()

        # Фильтруем список блюд по их id
        return [lunch for lunch in lunchs if lunch.id in lunch_id_list]

    def get_user_lunchs_text(self):
        """
        Функция возвращает текст с выбранными пользователями блюд, разделенными '\n'.

        """

        text = '\n'.join([lunch.name for lunch in self.get_user_lunchs_list()])
        if self.has_additionally():
            text += '\n' + self.additionally.strip()
        return text

    def has_additionally(self):
        """
        Функция вернет true, если additionally задано.
        Перед проверкой длины additionally, строка обрабатывается -- удаление пробелов,
        символов перехода и т.п. с начала и конца строки.

        """

        # TODO: завести getter / setter для вызова strip
        return len(self.additionally.strip()) > 0

    def __repr__(self):
        return "<OrderLunch(user_ip='{}', name='{}', order='{}', " \
               "lunch_id='{}', last_online_date='{}', " \
               "last_select_lunch_date='{}', additionally='{}')>".format(self.user_ip, self.name, self.order,
                                                                         self.lunch_id, self.last_online_date,
                                                                         self.last_select_lunch_date,
                                                                         self.additionally)


# TODO: при удалении, также удалять блюда из Lunchs
# http://docs.sqlalchemy.org/en/latest/orm/cascades.html
# http://stackoverflow.com/questions/5033547/sqlachemy-cascade-delete
class LunchInfo(db.Model):
    """
    Класс содержит информацию о меню используемую для проверки актуальности меню пользователем.

    """

    __tablename__ = 'LunchsInfo'

    # Уникальный номер меню.
    id = db.Column(db.Integer, primary_key=True)

    # Уникальный номер меню. Соответствует id письма, из которого было получено.
    lunch_id = db.Column(db.Integer, unique=True)

    # Заголовок к меню ланча, например: "Меню бизнес-ланча на пятницу"
    subject = db.Column(db.String)

    # Дата получения меню
    date = db.Column(db.DateTime)

    def __repr__(self):
        return "<LunchInfo(id='{}',lunch_id='{}', " \
               "subject='{}', date='{}')>".format(self.id, self.lunch_id, self.subject, self.date)


class Lunch(db.Model):
    """
    Класс описывает меню заказа.

    """

    __tablename__ = 'Lunchs'

    id = db.Column(db.Integer, primary_key=True)

    # Уникальный номер меню. Соответствует id письма, из которого было получено.
    lunch_id = db.Column(db.Integer, primary_key=True)

    # Название блюда
    name = db.Column(db.String)

    # Вес блюда. Может быть такого вида: "250 мл", "110 гр", "100/50 гр" и т.п.
    weight = db.Column(db.String)

    # Цена блюда. Может быть: "50 руб.", "45/55/55 руб." и т.п.
    price = db.Column(db.String)

    # Категория блюда. Может быть, например: Салаты, Супы, Горячее и т.п.
    category = db.Column(db.String)

    def __repr__(self):
        return "<Lunch(id='{}', name='{}', weight='{}', " \
               "price='{}', category='{}', lunch_id='{}')>".format(self.id, self.name, self.weight,
                                                                   self.price, self.category, self.lunch_id)


# TODO: думаю, нужно добавить и результат отправки, хотя вряд ли он будет неудачным
class OrderMenu(db.Model):
    """
    Класс описывает факт заказа меню.

    """

    __tablename__ = 'OrderMenus'

    id = db.Column(db.Integer, primary_key=True)

    # Пользователь, отправивший заказ
    user_ip = db.Column(db.String, nullable=False)

    # Уникальный номер меню. Соответствует id письма, из которого было получено.
    lunch_id = db.Column(db.Integer, nullable=False)

    # Дата и время отправки заказа
    date_time = db.Column(db.DateTime, nullable=False)

    # Текст письма с заказом
    text = db.Column(db.String, nullable=False, default='')

    class OrderMenuAlreadyExists(Exception):
        def __init__(self, order_menu):
            self.order_menu = order_menu

    def __init__(self, user_ip, lunch_id, text):
        # TODO: проверка заказа внутри одной группы пользователей
        # заказ будет отправлен без проблем разными пользователями,
        # но можно проверять, что заказ был отправл одним и только
        # одним админом из разрешенных в config.ip_admins

        # Проверка того, что такой заказ меню уже есть
        order_menu = OrderMenu.get(user_ip, lunch_id, text)
        if order_menu is not None:
            raise OrderMenu.OrderMenuAlreadyExists(order_menu)

        self.user_ip = user_ip
        self.lunch_id = lunch_id
        self.text = text

        from datetime import datetime
        self.date_time = datetime.today()

    # @staticmethod
    # def has(user_ip, lunch_id, text):
    #     """
    #     Функция возвращает True, если заказ <user_ip> меню <lunch_id> с текстом <text> уже есть в базе.
    #
    #     """
    #
    #     from app import session
    #     has = session.query(OrderMenu)\
    #         .filter(OrderMenu.user_ip == user_ip)\
    #         .filter(OrderMenu.lunch_id == lunch_id)\
    #         .filter(OrderMenu.text == text)\
    #         .exists()
    #     has = session.query(db.literal(True)).filter(has).scalar()
    #     return True == has

    # @staticmethod
    # def has(user_ip, lunch_id, text):
    #     return OrderMenu.get(user_ip, lunch_id, text) is not None

    @staticmethod
    def get(user_ip, lunch_id, text):
        """
        Функция возвращает True, если заказ <user_ip> меню <lunch_id> с текстом <text> уже есть в базе.

        """

        from app import session
        return session.query(OrderMenu)\
            .filter(OrderMenu.user_ip == user_ip)\
            .filter(OrderMenu.lunch_id == lunch_id)\
            .filter(OrderMenu.text == text)\
            .one_or_none()

    def __repr__(self):
        return "<OrderMenu(id='{}', user_ip='{}', lunch_id='{}', date_time='{}', text='{}')>".format(
            self.id, self.user_ip, self.lunch_id, self.date_time, self.text
        )


# Для создание базы если ее нет
db.create_all()

if __name__ == '__main__':
    from app import session
    # for user in session.query(UserOrderLunch).all():
    #     print(user.user_ip, user.name)

    for _ in session.query(OrderMenu).all():
        print(_.id, _.user_ip, _.lunch_id, _.date_time)
