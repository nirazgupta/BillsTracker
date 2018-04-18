from flask import Flask, Blueprint, jsonify
from flask import Flask, render_template, flash, redirect, url_for, g, session, logging, request
from passlib.hash import sha256_crypt
from functools import wraps
from sqlalchemy.orm import sessionmaker
from jinja2 import Environment, PackageLoader, select_autoescape
from .form import RegisterForm, TransactionForm, EditTransForm, EmailForm, PasswordForm
from it680vizapp import mysql, mail, serialize
from flask_mail import Message
#from mysql import escape_string as thwart
from flask import current_app
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
import pandas as pd
import json
import datetime as dt
from flask_paginate import Pagination, get_page_parameter


#from wapy.api import Wapy
#from walmart_api_client import WalmartApiClient
import pandas.io.sql as psql
from it680vizapp.group.routes import get_users_id

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

#Site blue print
mod = Blueprint('site', __name__, template_folder='templates', static_url_path='/site/static', static_folder='./static')
default_breadcrumb_root(mod, '.')


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
        	flash('Not logged in, Please login first.','danger')
        	return redirect(url_for('site.login'))
    return wrap




#Index route 
@mod.route('/')
# @register_breadcrumb(mod, '.', 'Home')
def index():
	return render_template('site/index.html')

#Site homepage route
@mod.route('/home')
@register_breadcrumb(mod, '.', 'Home', order=0)
def home():
	return render_template('site/index.html')


#Site about page route
@mod.route('/about')
@register_breadcrumb(mod, '.about', 'About', order=5)
def about():
	return render_template('site/about.html')

#Site contact page route
@mod.route('/contact')
# @register_breadcrumb(mod, '.', 'Contact')
def contact():
	return render_template('site/contact.html')

@mod.route('/viz')
def viz():
	return render_template('site/viz.html')


@mod.route('/getdata')
@login_required
def getdata():
	conn = mysql.connection
	cur = mysql.connection.cursor()
	group_id = session['group_id']
	
	query_trans = ''' SELECT sum(ut.share_amount) as amount, t.item
					FROM user_transaction ut
					join transaction t on t.transaction_id = ut.transaction_id
					where t.group_id = %s
					group by t.item
					order by t.item '''

	cur.execute(query_trans, group_id)
	result = cur.fetchall()
	# current_app.logger.info(result)
	# current_app.logger.info(result)

	#df2 = psql.read_sql(query_trans, group_id, conn)
	#df_to_json2 = df2.to_json(orient='records')

	#result = cur.execute(query_trans)
	cur.close()
	return jsonify(result)

@mod.route('/get_user_chart_data')
@login_required
def get_user_chart_data():
	conn = mysql.connection
	cur = mysql.connection.cursor()
	group_id = session['group_id']
	
	query_trans = ''' SELECT  u.fname as name, u.user_id, sum(ut.share_amount) as amount
					FROM user u
					join user_transaction ut on ut.user_id = u.user_id
					join transaction t on t.transaction_id = ut.transaction_id
					where t.group_id = %s
					group by u.fname
					order by u.fname '''
	cur.execute(query_trans, group_id)
	result = cur.fetchall()
	cur.close()
	return jsonify(result)

@mod.route('/get_user_chart_data2', methods=['GET', 'POST'])
@login_required
def get_user_chart_data2():
	if request.method == 'POST':
		user_id = request.form['user']
		conn = mysql.connection
		cur = mysql.connection.cursor()
		group_id = session['group_id']
		
		query_trans = ''' SELECT sum(ut.share_amount) as amount, t.item
					FROM user_transaction ut
					join transaction t on t.transaction_id = ut.transaction_id
					where t.group_id = %s and ut.user_id = %s
					group by t.item
					order by t.item '''
		cur.execute(query_trans, ([group_id, user_id]))
		result = cur.fetchall()
		current_app.logger.info(result)
		cur.close()
		return jsonify(result)


@mod.route('/lineChart', methods=['GET', 'POST'])
@login_required
def lineChart():
	if request.method == 'POST':
		user_id = request.form['user']
		conn = mysql.connection
		cur = mysql.connection.cursor()
		group_id = session['group_id']
		
		query_trans = ''' SELECT  u.fname as name, t.manual_date as date, ut.share_amount as amount
						FROM user u
						join user_transaction ut on ut.user_id = u.user_id
						join transaction t on t.transaction_id = ut.transaction_id
						where t.group_id = %s and ut.user_id = %s
						order by t.manual_date
						'''

		cur.execute(query_trans, ([group_id, user_id]))
		result = cur.fetchall()

		format_data = []
		for item in result:
			name = item['name']
			date = item['date'].strftime('%Y-%m-%d %H:%M')
			amount = item['amount']
			format_data.append({'name':name, 'date': date, 'amount':amount})
		current_app.logger.info(format_data)
		cur.close()
		return jsonify(format_data)

############### BELOW ARE CODE FOR USER AUTH, EXPENSE MANAGEMENT ########################

#Wrap session for logged in access to pages


#wrapper for setting role based access for site
# def roles_required(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         user = session['username']
#         cur = mysql.connection.cursor()
#         #Get username
#         role_query_statement = ''' select u.name, u.username, g.group_name, g.group_id, u.password
#         						 from user u join user_group g on g.user_id = u.user_id 
#         						 having u.username = %s '''

#         result = cur.execute(role_query_statement, [user])
        
#         user_data = cur.fetchone()
#         user_auth = user_data['authority']
#         if user_auth in ['Admin', 'admin', 'member']:
#             return func(*args, **kwargs)
#         else:
#             flash('You do not have access to content of this page, redirected to dashboard', 'danger')
#             return redirect(url_for('site.login'))
#     return wrapper




@mod.route('/register', methods= ['GET', 'POST'])
# @register_breadcrumb(mod, '.', 'Signup')
@register_breadcrumb(mod, '.register', 'Signup')
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		fname = form.fname.data.strip()
		lname = form.lname.data.strip()
		email = form.email.data.strip().lower()
		username = form.username.data.strip().lower()
		password = sha256_crypt.encrypt(str(form.password.data))
		enabled = False

		name = fname + ' ' + lname 

		#create a cursor
		cur = mysql.connection.cursor()

		#query to check if user already exists
		reg_query_username = ''' select username from user where username = %s '''
		cur.execute(reg_query_username, ([username]))

		existing_user = cur.fetchone()
		current_app.logger.info(existing_user)
		#logic to check if user already exists, if not, the insert logics will execute
		if existing_user is None:
			register_insert_query = ''' INSERT INTO user (name, fname, lname, email, username, password, enabled)
										 VALUES(%s, %s, %s, %s, %s, %s, %s) '''
			cur.execute(register_insert_query, (name, fname, lname, email, username, password, enabled))
			mysql.connection.commit()

			enabled_username_query = ''' select username, enabled from user where username = %s '''
			cur.execute(enabled_username_query, ([username]))

			user_data = cur.fetchone()
			enabled_fetch = user_data['enabled']

			if enabled_fetch == 0:
				token = serialize.dumps(email, salt='My-Token')
				current_app.logger.info(token)

				#prepare email msg
				email_msg = Message('Confirm Email', sender='gupta.niraz@gmail.com', recipients=[email])
				link = url_for('site.confirm_email', token=token, _external=True)

				email_msg.body = 'Your link is {}'.format(link)
				mail.send(email_msg)

				flash('Resistration Successful. Please check your email for activation.', 'success')
				return render_template('site/index.html', data=token)
			#redirect(url_for('site.index'))

			#close cursor
			cur.close()
		else:
			flash('User already exits!', 'danger')
	
	# mysql.connection.close()
	return render_template('site/register.html', form=form)


@mod.route('/confirm_email/<token>')
def confirm_email(token):
	try:
		email = serialize.loads(token, salt = 'My-Token', max_age=86400)
	except SignatureExpired:
		return '<h1>The token has expired!</h1>'
	# return '<h1>The token works!</h1>'
	cur = mysql.connection.cursor()
	first_query = ''' SELECT username, enabled from user where email = %s '''
	cur.execute(first_query, ([email]))
	user_data = cur.fetchone()
	user_status = user_data['enabled']
	
	user_name = user_data['username']
	current_app.logger.info(user_status)
	current_app.logger.info(user_name)

	if user_status == True:
		flash('Already activated', 'success')
		session['logged_in'] = True
		session['username'] = user_name
		return redirect(url_for('site.dashboard'))
	else:

		query = '''UPDATE user SET enabled = %s WHERE email = %s'''
		cur.execute(query, (True, [email]))
		mysql.connection.commit()

		flash('Account activated', 'success')
		session['logged_in'] = True
		session['username'] = user_name
	return redirect(url_for('site.dashboard'))

@mod.route('/reset', methods= ['GET', 'POST'])
def password_reset():
	form = EmailForm(request.form)
	if form.validate():
		email = form.email.data.strip()

		cur = mysql.connection.cursor()
		query = '''SELECT * from user WHERE email=%s'''
		cur.execute(query, [email])
		user = cur.fetchone()

		token = serialize.dumps(email, salt='recover_password_key_token')
		current_app.logger.info(token)

		#prepare email msg
		email_msg = Message('Password reset requested', sender='gupta.niraz@gmail.com', recipients=[email])
		link = url_for('site.password_reset_token', token=token, _external=True)

		email_msg.body = 'Please click on the link to change your password {}'.format(link)
		mail.send(email_msg)

		msg = 'A link for password change request has been sent to your Inbox.'
		return render_template('site/index.html', msg=msg)

	return render_template('site/password_reset.html', form=form)


@mod.route('/reset/<token>', methods=["GET", "POST"])
def password_reset_token(token):
	try:
		email = serialize.loads(token, salt = 'recover_password_key_token', max_age=86400)
	except SignatureExpired:
		return '<h1>The token has expired!</h1>'

	form = PasswordForm(request.form)

	if form.validate():
		cur = mysql.connection.cursor()
		fetch_query = '''SELECT username, enabled from user where email = %s'''
		cur.execute(fetch_query, ([email]))
		user_data = cur.fetchone()

		user_status = user_data['enabled']
		user_name = user_data['username']

		new_password = sha256_crypt.encrypt(str(form.password.data))
		current_app.logger.info(new_password)
		pass_query = '''UPDATE user SET password = %s WHERE email = %s'''
		cur.execute(pass_query, (new_password, [email]))

		mysql.connection.commit()
		flash('Password change successful. You can login now.', 'success')
		# msg = 'Password change successful. You can login now.'
		return redirect(url_for('site.login'))
	return render_template('site/pass_reset_token.html', form=form, token=token)



#User Login process and conditional routes to user login page and dashboard
@mod.route('/login', methods = ['GET','POST'])
# @register_breadcrumb(mod, '.', 'Login')
@register_breadcrumb(mod, '.login', 'Login')
def login():
	if 'logged_in' in session:
		return redirect(url_for('site.dashboard'))

	elif request.method == 'POST':
		#Get data from login form
		#name = request.form['name']
		username = request.form['username']
		form_pass = request.form['password']

		#login cursor
		cur = mysql.connection.cursor()

		#Get username
		admin_login = '''select name, username, password, super_user, enabled from user where username = %s'''
		# group_query = ''' select u.enabled, u.name, u.username, u.password, a.authority
		# 						 from user u join authorities a on a.user_id = u.user_id
		# 						  having u.username = %s '''
		user_result = cur.execute(admin_login, ([username]))
		user_data = cur.fetchone()

		if user_result > 0:
			#get stored hash
			users_name = user_data['name']
			user_name = user_data['username']
			user_pass = user_data['password']
			super_user = user_data['super_user']
			enabled = user_data['enabled']
            
			#Compare pass
			if user_name:
				if sha256_crypt.verify(form_pass, user_pass) == False:
					flash('password do not match!', 'danger')
					return render_template('site/login.html')
				elif enabled == False:
					flash('Your account is inactive!', 'danger')
					return render_template('site/login.html')

				else:
					# if username = user_name
					session['logged_in'] = True
					session['username'] = username
					#session['authority'] = member
					session['name'] = users_name
					session['super_user'] = super_user
					#session['name'] = users_fullname

					if session['super_user'] is True:
						flash('Welcome' + ' ' + users_name, 'success')
						return redirect(url_for('cms.dashboard'))
					else:
						flash('Welcome ' + ' ' + users_name, 'success')
						return redirect(url_for('site.dashboard'))

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


#Route to dashboard
@mod.route('/dashboard')
@login_required
@register_breadcrumb(mod, '.dashboard', 'Dashboard', order=4)
def dashboard():
	cur = mysql.connection.cursor()
	username = session['username']
	query = """
			select user_id from user where username=%s
			"""
	cur.execute(query,([username]))
	_usr_id = cur.fetchone()
	usr_id = _usr_id['user_id']
	total_amt_data = get_total_bal(usr_id)
	total_lent_data = get_lent_bal(usr_id)
	total_expense_data = get_expense_bal(usr_id)
	current_app.logger.info(total_expense_data)
	data = {"total":total_amt_data, "lent":total_lent_data, "expense":total_expense_data}
	
	return render_template('site/dashboard.html', result=data)

def get_total_bal(user_id):
	cur = mysql.connection.cursor()
	query = """
			select sum(amount) as total_bal 
			from transaction 
			where user_id=%s and status='unpaid'
			"""
	cur.execute(query, ([user_id]))
	data=cur.fetchone()
	return data

def get_lent_bal(user_id):
	cur = mysql.connection.cursor()
	query = """
			select sum(you_lent) as lent_bal 
			from transaction  
			where user_id=%s and status='unpaid'
			"""
	cur.execute(query, ([user_id]))
	data=cur.fetchone()
	return data

def get_expense_bal(user_id):
	cur = mysql.connection.cursor()
	query = """
			select sum(share_amount) as shr_amount 
			from user_transaction ut join transaction t 
			on t.transaction_id = ut.transaction_id
			where ut.user_id=%s and status='unpaid'
			"""
	cur.execute(query, ([user_id]))
	data=cur.fetchone()
	current_app.logger.info(data)
	return data

#Transaction prcess and routes to new transaction page
@mod.route('/trans_form', methods= ['GET', 'POST'])
@login_required
#@roles_required
# @register_breadcrumb(mod, '.trans_form', 'NewEntry', order=4)
def TransactionEntry():
	#Get user from db
	cur = mysql.connection.cursor()

	group_id = session['group_id']
	current_app.logger.info(group_id)
	sql_user_auth_query = ''' select u.user_id, u.name, u.username, tg.group_name, ug.group_id
								from user u join user_group ug on ug.user_id = u.user_id 
								join tbl_group tg on ug.group_id = tg.group_id
								having ug.group_id = %s; '''
	cur.execute(sql_user_auth_query, ([group_id]))
	result = cur.fetchall() 
	

	form = TransactionForm(request.form)
	if request.method == 'POST' and form.validate():
		comment = form.description.data
		manual_date = form.manual_date.data
		item = form.item.data
		#payer = form.payer.data
		#payer = request.form['payer']
		amount = form.amount.data
		#status = form.status.data
		status = request.form['status']

		user = session['username']
		_usr_data = get_users_id([user])
		usr_id = _usr_data['user_id']

		selected_users = request.form.getlist('person')
		current_app.logger.info(item) 
		
		#create a cursor
		if len(selected_users) == 0:
			flash('Please select atleast one member!', 'danger')
		else:
			cur = mysql.connection.cursor()
			tran_form_insert_query = ''' INSERT INTO transaction(group_id, user_id, comment, item, amount, status, manual_date)
										 VALUES(%s, %s, %s, %s, %s, %s, %s) '''
			cur.execute(tran_form_insert_query, (group_id, usr_id, comment, item, amount, status, manual_date))
			mysql.connection.commit()

		
			#converted the user_id to integer by counting
			list_count = []
			for users in selected_users:
				list_count.append(selected_users.count(users))
			current_app.logger.info(list_count)

			#summed the counted users in the list
			sum_users = 0
			for item in list_count:
				sum_users += item
			current_app.logger.info(sum_users)
			#person_name = request.form[]

			#Now divided the total amount by the sum of counted users
			_share = amount/sum_users
			each_share = round(_share, 2)
			current_app.logger.info(each_share)

			#Repeated the share amount into a list equivalent to number of users e.g. 10 is now [10,10,10,10]
			rep_list = [each_share] * sum_users
			current_app.logger.info(rep_list) 
			
			#The amount lent by the payer
			_lent = _share - amount
			current_app.logger.info(_lent)
			
			#fetch max transaction id from transaction table
			tran_form_max_trans_id = ''' select MAX(transaction_id) from transaction '''
			cur.execute( tran_form_max_trans_id )
			tran_id = cur.fetchone()

			#Convert tran_id from list to usable ID
			tran_id_val = 0
			for key, val in tran_id.items():
				tran_id_val += val
			current_app.logger.info(tran_id_val)

			#converted the transaction id into a list and repeated by number of person
			tran_id_list = [tran_id_val] * sum_users
			current_app.logger.info(tran_id_list)


			#Everything is working till here.
			#zipped the three lists altogether
			zipAll = zip(selected_users, tran_id_list, rep_list)
			current_app.logger.info(zipAll)

			for x, y, z in zipAll:
			    format_str = """INSERT INTO user_transaction (user_id, transaction_id, share_amount)
			    VALUES ({user_id}, '{transaction_id}', '{share_amount}'); """

			    sql_command = format_str.format(user_id=x, transaction_id=y, share_amount=z)
			    current_app.logger.info(sql_command)
			    cur.execute(sql_command)
			
			#Update the amt_lent column in user_transaction by matching the transaction id and user_id
			tran_update_amtlent_query = ''' UPDATE transaction SET you_lent=%s WHERE transaction_id = %s and user_id = %s '''
			cur.execute(tran_update_amtlent_query, (_lent, tran_id_val, usr_id))

			#Update the per_share in user_transaction by matching the transaction id and user_id
			tran_update_pershare_query = ''' UPDATE transaction SET your_share=%s WHERE transaction_id = %s and user_id = %s '''
			cur.execute(tran_update_pershare_query, (_share, tran_id_val, usr_id))

			mysql.connection.commit()
			#*********************

			flash('Record inserted!', 'success')
			#redirect(url_for('site.TransactionEntry', grp=group_id))
			render_template('site/transaction_form.html', form=form, grp=group_id)

			#close cursor
			cur.close()
		#mysql.connection.close()
	return render_template('site/transaction_form.html', form=form, data=result)



#Transactions view process and route to transaction view page
@mod.route('/user_trans_view', methods= ['GET', 'POST'])
@register_breadcrumb(mod, '.trans_view.user_trans_view', 'TransDetail')
@login_required
def user_trans_view():
	user = session['username']
	cur = mysql.connection.cursor()
	status = ''
	if request.method == 'POST':
		stat = request.form['status']
		status += stat

	query_trans = ''' SELECT ut.id, t.entry_date, count(ut.user_id) as user_count, sum(ut.share_amount) as shr_amount, 
						t.item, t.status, t.payer
					FROM user_transaction ut
					join transaction t on t.id = ut.id
					group by ut.id 
					having t.status LIKE %s 
					order by ut.id '''
	result = cur.execute(query_trans, ([status]))
	result_2 = cur.fetchall()


	query_lent_share_calc = ''' SELECT distinct ut.user_id, sum(ut.per_share) as per_share,
					sum(ut.amt_lent) as amt_lent, sum(ut.share_amount) as share_amt, u.name
					from user_transaction as ut
					inner join 
					(
						select status, id
						from transaction
						WHERE status = %s
					) as b
					on ut.id=b.id
					inner join 
					(
						select user_id, name
						from user
					) as u
					on ut.user_id=u.user_id
					GROUP by ut.user_id 
					order by u.name '''
	cur.execute(query_lent_share_calc, ([status]))
	result_4 = cur.fetchall()

	query_trans_new = """ SELECT SUM(amount) as amount, payer FROM transaction 
						WHERE status LIKE %s
						GROUP BY payer """
	cur.execute(query_trans_new, ([status]))
	result_3 = cur.fetchall()


	tran_view_user_role = ''' SELECT username, authority 
								from user u join authorities a on u.user_id = a.user_id
								having username = %s '''
	user_role = cur.execute(tran_view_user_role, ([user]))
	user_role_data = cur.fetchone()
	user_auth = user_role_data['authority']

	if result > 0 and user_auth in ['member', 'admin', 'Admin']:
		return render_template('site/user_trans_view.html', data_2=result_2, data_3=result_3, data_4=result_4)
	else:
		msg = 'No data found or you do not have enough privilege.'
		return render_template('site/user_trans_view.html', msg=msg)
	
	#commit
	mysql.connection.commit()
	#close conn
	cur.close()
	mysql.connection.close()



#Update status of transaction
@mod.route('/update_status', methods=['GET', 'POST'])
@login_required
def update_status():
	if request.method == 'POST':
		get_status = request.form['status']
		transaction_id = request.form['transaction_id']
		conn = mysql.connection
		cur = mysql.connection.cursor()
		group_id = session['group_id']
		
		# query_trans = ''' SELECT sum(ut.share_amount) as amount, t.item
		# 			FROM user_transaction ut
		# 			join transaction t on t.transaction_id = ut.transaction_id
		# 			where t.group_id = %s and ut.user_id = %s
		# 			group by t.item
		# 			order by t.item '''
		# cur.execute(query_trans, ([group_id, user_id]))
		# result = cur.fetchall()
		current_app.logger.info(get_status)
		current_app.logger.info(transaction_id)
		# cur.close()
		return 'Success'




#Change role of user -- not working yet
@mod.route('/edit_transaction/<string:transaction_id>', methods=['GET', 'POST'])
@login_required
#@roles_required
def edit_transaction(transaction_id):
	form = TransactionForm(request.form)
	group_id = session['group_id']

	cur = mysql.connection.cursor()
	tran_result = cur.execute("SELECT * FROM transaction where transaction_id = %s", ([transaction_id]))
	tran_data = cur.fetchone()
	
	form.description.data = tran_data['comment']
	form.manual_date.data = tran_data['manual_date']
	form.item.data = tran_data['item']
	form.status.data = tran_data['status']
	

	if request.method == 'POST' and form.validate():
		status = request.form['status']
		comment = request.form['description']
		new_date = request.form['manual_date']
		new_item = request.form['item']

		current_app.logger.info(new_date)
		current_app.logger.info(new_item)


		cur = mysql.connection.cursor()

		status_update_query = ''' UPDATE transaction SET status=%s, comment=%s, item=%s, manual_date=%s WHERE transaction_id = %s '''
		cur.execute(status_update_query, (status, comment , new_item, new_date, transaction_id))


		mysql.connection.commit()
		cur.close()
		flash('Update successful', 'success')
		return redirect(url_for('group.transactions', group_id=group_id))
	return render_template('site/edit_transaction.html', form=form)


#Delete transaction
@mod.route('/delete_transaction/<string:transaction_id>', methods=['GET', 'POST'])
@login_required
#@roles_required
def delete_transaction(transaction_id):

	username = session['username']
	_usr_data = get_users_id([username])
	usr_id = _usr_data['user_id']

	group_id = session['group_id']

	current_app.logger.info(group_id)

	cur = mysql.connection.cursor()
	query = """ select user_id, group_id, group_admin
				from user_group 
				where user_id=%s and group_id=%s """
	cur.execute(query, ([usr_id, group_id]))
	result = cur.fetchone()
	current_app.logger.info(result['group_admin'])

	if result['group_admin'] == 1:
		
		# Create a trigger to keep record of deleted transactions

		cur.execute("DELETE FROM user_transaction WHERE transaction_id=%s", [transaction_id])
		cur.execute("DELETE FROM transaction WHERE transaction_id=%s", [transaction_id])
		mysql.connection.commit()

		cur.execute("SELECT * FROM transaction where transaction_id = %s", [id])
		deleted_id = cur.fetchone()
		if deleted_id is None:
			flash("Transaction is deleted", 'success')
			return redirect(url_for('group.transactions', group_id=group_id))
		else:
			flash("Query is not working", 'danger')
			return redirect(url_for('group.transactions', group_id=group_id))
	flash('You cannot delete this bill', 'danger')
	return redirect(url_for('group.transactions', group_id=group_id))


#Logout process by clearing session
@mod.route('/logout')
def logout():
	# for key in session.keys():
	# 	session.pop(key)
	session.clear()

	flash('You are logged out', 'success')
	return redirect(url_for('site.login'))

