from it680vizapp import app 
# from flask import Flask
# from flask_mysqldb import MySQL
# if __name__ == '__main__':
app.jinja_env.auto_reload = True

app.config["CACHE_TYPE"] = "null"

#cache.init_app(app)
app.config['TEMPLATES_AUTO_RELOAD']=True

if __name__ == '__main__':
	app.run() 