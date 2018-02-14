import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# Config = {
# 	'DEFUALT': Default,
# 	'DEVELOPMENT': Development,
# 	'PRODUCTION': Production,
# 	'TESTING': Testing

# }

# class Development(Default):
# 	DEBUG = True
# 	DEVELOPMENT = True
# 	SECRET_KEY = 'lenovoideapad123456789'
# 	# FLASK_HTPASSWD_PATH = '/secret/.htpasswd'
# 	# FLASK_SECRET = SECRET_KEY
# 	MYSQL_HOST = 'localhost'
# 	MYSQL_USER = 'root'
# 	MYSQL_PASSWORD = 'motorockr'
# 	MYSQL_DB = 'flask_mankatoexpenses'
# 	MYSQL_CURSORCLASS = 'DictCursor'

# class Production(Default):
# 	pass

# class Testing(Default):
# 	TESTING = True


# DEBUG = True

# SECRET_KEY = 'lenovoideapad123456789'

# MYSQL_HOST = 'localhost'
# MYSQL_USER = 'root'
# MYSQL_PASSWORD = 'motorockr'
# MYSQL_DB = 'flask_mankatoexpenses'
# MYSQL_CURSORCLASS = 'DictCursor'


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'lenovoideapad123456789'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'motorockr'
    MYSQL_DB = 'flask_mankatoexpenses'
    MYSQL_CURSORCLASS = 'DictCursor'

    SECURITY_PASSWORD_SALT = '\xd3\xff\xc0\xa0\xe8\x11\x0b\xb9\x93\xb2'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'gupta.niraz@gmail.com'
    MAIL_PASSWORD = 'motorockr'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

class ProductionConfig(Config):
    DEVELOPMENT = False
    SECRET_KEY = '\xd3\xff\xc0\xa0\xe8\x11\x0b\xb9\x93\xb2\xd0\x97\xe4\x1b\xf2\x12\x81\xd2'
    DEBUG = False
    MYSQL_HOST = 'us-cdbr-iron-east-05.cleardb.net'
    MYSQL_USER = 'b194ad3dc22123'
    MYSQL_PASSWORD = 'a55890a8'
    MYSQL_DB = 'heroku_0a9ab04112f0d49'
    MYSQL_CURSORCLASS = 'DictCursor'

    SECURITY_PASSWORD_SALT = '\xd3\xff\xc0\xa0\xe8\x11\x0b\xb9\x93\xb2'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'gupta.niraz@gmail.com'
    MAIL_PASSWORD = 'motorockr'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
	
   # DB_HOST = 'my.production.database'