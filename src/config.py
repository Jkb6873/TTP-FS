import os

APP_SECRET = os.environ.get("APP_SECRET")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
IEX_PREFIX = os.environ.get("IEX_PREFIX")
TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'frontend/build')
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'frontend/build/static')
