from flask import Flask, Blueprint
# from flask_restful import restful
from flask import Flask, render_template, flash, redirect, url_for, g, session, logging, request
from flask_mysqldb import MySQL
from _mysql import escape_string as thwart
# from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DecimalField, DateField
from passlib.hash import sha256_crypt
from functools import wraps
# from sqlalchemy import create_engine
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from jinja2 import Environment, PackageLoader, select_autoescape
#main = Blueprint('main', __name__, template_folder='templates')
from flask_mysqldb import MySQL

#app = Flask(__name__)

app = Flask(__name__, static_url_path='/static', template_folder='templates')
#app.config.from_object('config.Config')
#app.config.from_pyfile('config.py')
	
db = MySQL(app)


#mod = Blueprint('site', __name__, template_folder='templates')

# @main.route('/')
# def index():
#     return "Main"


# from flask import Flask
# from flask_mysqldb import MySQL
# if __name__ == '__main__':


# main creation
#main = Flask(__name__)


# admin = Admin(main, name='main')
# mysql = SQLAlchemy(main)

#Config MySQL
#main.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:motorockr@localhost/flask_mankatoexpenses'
# engine = create_engine('mysql://root:motorockr@localhost/flask_mankatoexpenses')
# sql_session = sessionmaker(bind=engine)

# main.config['MYSQL_HOST'] = 'localhost'
# main.config['MYSQL_USER'] = 'root'
# main.config['MYSQL_PASSWORD'] = 'motorockr'
# main.config['MYSQL_DB'] = 'flask_mankatoexpenses'
# main.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Initialize database
# mysql = MySQL(main)

#Session.configure(bind=mysql)

@app.route('/')
def index():
	return "THIS IS TEST"

@app.route('/home')
def home():
	return render_template('site/index.html')

@app.route('/about')
def about():
	return render_template('site/about.html')

@app.route('/contact')
def contact():
	return render_template('site/contact.html')


#Wrap session
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
        	flash('Not logged in, Please login first.','danger')
        	return redirect(url_for('login'))
    return wrap

#Route to dashboard
@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html')


# # Resister form
# class RegisterForm(Form):
# 	name = StringField('Name', [validators.Length(min=1, max=50)])
# 	username = StringField('Username', [validators.Length(min=4, max=25)])
# 	email = StringField('Email', [validators.Length(min=6, max=50)])
# 	password = PasswordField('Password', [
# 		validators.DataRequired(),
# 		validators.EqualTo('confirm', message='Password do not mathc')
# 		])
# 	confirm = PasswordField('Confirm Password')

#Registration
@app.route('/register', methods= ['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#create a cursor
		conn = mysql.connection()
		cur = conn.cursor()
		existing_user = cur.execute("select username, password from users where username = %s", (thwart([username])))

		if existing_user is None:
			try:
				cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (thwart(name), thwart(email), thwart(username), thwart(password)))
				flash('Resistration Successful!', 'success')
				redirect(url_for('index'))
			except Exception as e:
				return str((e))
		#commit
		conn.commit()

		#close cursor
		
		flash('User already exits!', 'danger')
		cur.close()
		conn.close()
	return render_template('site/register.html', form=form)

#admin.add_view(ModelView(register, mysql.sql_session))

#Login
@app.route('/login', methods = ['GET','POST'])
def login():
	if request.method == 'POST':
		#Get data from login form
		#name = request.form['name']
		username = request.form['username']
		form_pass = request.form['password']

		#login cursor

		cur = mysql.connection.cursor()

		#Get username
		result = cur.execute("select name, username, password from users where username = %s", ([username]))
		user_data = cur.fetchone()
		if result > 0:
			#get stored hash
			users_fullname = user_data['name']
			user_name = user_data['username']
			user_pass = user_data['password']
			#Compare pass
			if user_name:
				if sha256_crypt.verify(form_pass, user_pass) == False:
					flash('password do not match!', 'danger')
					return render_template('site/login.html')

				else:
					# if username = user_name
					session['logged_in'] = True
					session['username'] = username
					#session['name'] = users_fullname

					flash('Welcome', 'success')
					return redirect(url_for('dashboard'))
					# return render_template('index.html')
					mysql.connection.commit()
			else:
				error = '.'
				return render_template('site/login.html', error=error)				

		else:
			error = 'User not found.'
			return render_template('site/login.html', error=error)

		cur.close()
		mysql.connection.close()
	return render_template('site/login.html')

#Logout
@app.route('/logout')
def logout():
	session.clear()
	flash('You are logged out', 'success')
	return redirect(url_for('login'))

# # Transaction Entry form
# class TransactionForm(Form):
# 	comment = TextAreaField('comment', [validators.Length(min=3, max=200)])
# 	entry_date = DateField('entry_date', format='%m/%d/%Y') 
# 	#DateField('entry_date', format='%y/%m/%d')
# 	item = StringField('item', [validators.Length(min=4, max=101)])
# 	payer = StringField('payer', [validators.Length(min=3, max=51)])
# 	amount = DecimalField('amount')
# 	status = StringField('status', [validators.Length(min=1, max=15)])

#Transaction form
@app.route('/trans_form', methods= ['GET', 'POST'])
@login_required
def TransactionEntry():
	form = TransactionForm(request.form)
	if request.method == 'POST' and form.validate():
		comment = form.comment.data
		entry_date = form.entry_date.data
		item = form.item.data
		payer = form.payer.data
		amount = form.amount.data
		status = form.status.data

		#create a cursor
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO transaction(entry_date, comment, item, payer, amount, status) VALUES(%s, %s, %s, %s, %s, %s)", (entry_date, comment, item, payer, amount, status))

		#commit
		mysql.connection.commit()

		flash('Record inserted!', 'success')
		redirect(url_for('TransactionEntry'))

		#close cursor
		cur.close()
		mysql.connection.close()
	return render_template('site/transaction_form.html', form=form)

#Transactions
@app.route('/trans_view')
@login_required
def tran_view():
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM transaction")

	data = cur.fetchall()

	if result > 0:
		return render_template('site/transactions.html', data=data)
	else:
		msg = 'No data found.'
		return render_template('site/transactions.html', msg=msg)
	
	#commit
	mysql.connection.commit()
	#close conn
	cur.close()
	mysql.connection.close()

# #Mysql To Dataframe
# @main.route('/df')
# @login_required
# def df():
# 	cur = mysql.connection.cursor()
# 	df = pd.read_sql('select * from transaction', con = MySQL(main))

# 	return render_template('df.html')

# #Admin configuration
# @main.route('/administer')
# def administer():
# 	try:
# 		return render_template('admin/new_admin.html')
# 	except:
# 		flash('Page not found!', 'danger')
# 		return render_template('index.html')



# if __name__ == '__main__':
# 	main.secret_key = 'lenovoideapad123456789'
# 	main.run(debug=True)

if __name__ == '__main__':
	#app.jinja_env.auto_reload = True
	#app.config['TEMPLATES_AUTO_RELOAD']=True
	app.run(debug=False) 
