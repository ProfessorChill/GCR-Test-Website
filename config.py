import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PFUDOR'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'postgresql+psycopg2://postgres:wwssadadba@localhost/gcr_test_site'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_IP = os.environ.get('ADMIN_IP') or '127.0.0.1'
