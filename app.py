#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from flask import Flask
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

# TODO: app.debug нужно неявно в config описать: DEBUG
import config
app.debug = config.debug_bd

db = SQLAlchemy(app)
session = db.session

# TODO: using app.logger
if config.debug:
    import logging
    import sys

    # # Попытка обойти ошибку UnicodeEncodeError в logging
    # class EncodingFormatter(logging.Formatter):
    #     def __init__(self, fmt, datefmt=None, encoding=None):
    #         logging.Formatter.__init__(self, fmt, datefmt)
    #         self.encoding = encoding
    #
    #     def format(self, record):
    #         result = logging.Formatter.format(self, record)
    #
    #         try:
    #             result = result.encode(sys.stdout.encoding, errors="replace").decode()
    #             # print(result)
    #         except Exception as e:
    #             # result = result.encode("UTF-8", errors="replace")
    #             print('@', e)
    #
    #         return result + "!!!"
    #
    # format = '[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s'
    #
    # stream_handler = logging.StreamHandler(stream=sys.stdout)
    # stream_handler.setFormatter(EncodingFormatter(format))
    #
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format=format,
    #     handlers=[
    #         logging.FileHandler(config.config_file_name, encoding='utf8'),
    #         stream_handler,
    #     ],
    # )

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s',
        handlers=[
            logging.FileHandler(config.config_file_name, encoding='utf8'),
            logging.StreamHandler(stream=sys.stdout),
        ],
    )
