import os
from flask import Flask
from flask_mysqldb import MySQL
from flask_breadcrumbs import Breadcrumbs
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.config.from_object('config.Config')
mysql = MySQL(app)
Breadcrumbs(app=app)

mail = Mail(app)
serialize = URLSafeTimedSerializer(app.config['SECRET_KEY'])

from it680vizapp.site.routes import mod
from it680vizapp.cms.routes import mod
from site import *
from it680vizapp.cms import *

# app.register_blueprint(site_blueprint)
# app.register_blueprint(admin)
app.register_blueprint(cms.routes.mod)
# app.register_blueprint(site.routes.mod, url_prefix = '/')
# app.register_blueprint(site.routes.mod, url_prefix = '/home')
app.register_blueprint(site.routes.mod)

# app.register_blueprint(admin.routes.mod, url_prefix = '/admin')
# app.register_blueprint(admin.routes.mod, url_prefix = '/admin/dashboard')

# app.register_blueprint(main)
# app.register_blueprint(admin)



