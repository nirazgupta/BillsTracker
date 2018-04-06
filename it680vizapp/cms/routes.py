from flask import Blueprint
from flask import Flask, render_template
from flask import Flask, render_template, flash, redirect, url_for, g, session, logging, request
from .form import RegisterForm, TransactionForm, EditUserForm
from _mysql import escape_string as thwart
from functools import wraps
from passlib.hash import sha256_crypt
from it680vizapp import mysql
from flask import current_app


mod = Blueprint('cms', __name__, template_folder='templates', static_url_path='/cms/static', static_folder='./static')


#User Login process and conditional routes to user login page and dashboard
@mod.route('/admin', methods = ['GET','POST'])
def admin():
	if 'logged_in' in session:
		return redirect(url_for('cms.dashboard'))

	elif request.method == 'POST':
		#Get data from login form
		#name = request.form['name']
		username = request.form['username']
		form_pass = request.form['password']

		#login cursor
		cur = mysql.connection.cursor()
		#Get username
		result = cur.execute("select u.name, u.username, a.authority, u.password from users_v2 u join authorities a on a.user_id = u.user_id having u.username = %s", [username])
		user_data = cur.fetchone()
		
		if result > 0:
			#get stored hash
			users_fullname = user_data['name']
			user_name = user_data['username']
			user_pass = user_data['password']
			auth_data = user_data['authority']

			#Compare pass
			if user_name:				
				if sha256_crypt.verify(form_pass, user_pass) == False:
					flash('password do not match!', 'danger')
				# elif auth_data not in ['Admin', 'admin']:
				# 	flash('Access denied, not sufficient privilege!', 'danger')
				# 	return render_template('site/login.html')
				else:
					# if username = user_name
					session['logged_in'] = True
					session['username'] = username
					session['auth'] = auth_data

					flash('Welcome Admin' , 'success')
					return render_template('cms/dashboard.html', data=user_data)
					# return render_template('index.html')
					cur.close()
					mysql.connection.close()
			else:
				error = '.'
				return render_template('cms/login.html', error=error)				
		else:
			error = 'User not found.'
			return render_template('cms/login.html', error=error)
	return render_template('cms/login.html')



#Wrap session for logged in access to pages
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
	    if 'logged_in' in session:
	    	return f(*args, **kwargs)
	    else:
	    	flash('Not logged in, Please login first.','danger')
	    	return redirect(url_for('cms.admin'))
    return wrap


def roles_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = session['username']
        cur = mysql.connection.cursor()
        #Get username
        result = cur.execute("select super_user from user where username=%s", [user])
        user_data = cur.fetchone()

        user_auth = user_data['super_user']

        if user_auth > 0:
            return func(*args, **kwargs)
        else:
            flash('Access denied', 'danger')
            return redirect(url_for('site.login'))
    return wrapper



#Admin dashboard route
@mod.route('/admin/dashboard')
@login_required
@roles_required
def dashboard():
	return render_template('cms/dashboard.html')

#Clear admin session
@mod.route('/admin/logout')
def logout():
	session.clear()
	flash('You are logged out', 'success')
	return redirect(url_for('cms.admin'))

#route to view all users -- this is working
@mod.route('/admin/viewusers')
@login_required
@roles_required
def viewusers():
	cur = mysql.connection.cursor()
	user_result = cur.execute("SELECT * FROM user")
	users_data = cur.fetchall()

	if user_result > 0:
		msg = 'table data'
		return render_template('cms/show_users.html', data=users_data)
	else:
		msg = 'No user found.'
		return render_template('cms/show_users.html', msg=msg)

	mysql.connection.commit()
	#close conn
	cur.close()
	mysql.connection.close()


@mod.route('/admin/editrole/<string:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required
def editrole(user_id):
	cur = mysql.connection.cursor()
	cur_2 = mysql.connection.cursor()
	user_result = cur.execute("SELECT * FROM user where user_id = %s", [user_id])
	#user_auth_result = cur_2.execute("SELECT * FROM authorities where user_id = %s", [user_id])
	users_data = cur.fetchone()
	#user_auth = cur_2.fetchone()

	mysql.connection.commit()

	form = EditUserForm(request.form)

	form.enabled.data = users_data['enabled']
	#form.authority.data = user_auth['authority']

	return render_template('cms/edituser.html', u_data=users_data)#, u_auth=user_auth)

#Change role of user -- not working yet
@mod.route('/admin/edituser/<string:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required
def edituser(user_id):
	cur = mysql.connection.cursor()
	cur_2 = mysql.connection.cursor()
	user_result = cur.execute("SELECT * FROM user where user_id = %s", [user_id])
	#user_auth_result = cur_2.execute("SELECT * FROM authorities where user_id = %s", [user_id])
	users_data = cur.fetchone()
	#user_auth = cur_2.fetchone()


	mysql.connection.commit()

	form = EditUserForm(request.form)
	form.name.data = users_data['name']
	form.username.data = users_data['username']
	form.email.data = users_data['email']
	#form.authority.data = user_auth['authority']

	
	if request.method == 'POST' and form.validate():
		stat = request.form['enabled']
		if stat == 'active':
			enabled = 1
		elif stat == 'inactive':
			enabled = 0
				
		cur = mysql.connection.cursor()

		query_1 = ''' UPDATE user SET enabled = %s WHERE user_id = %s '''
		cur.execute(query_1, ([enabled], [user_id]))

		query_3 = ''' SELECT enabled from users_v2 where user_id = %s '''
		cur.execute(query_3, ([user_id]))

		enabled_new = cur.fetchone()

		mysql.connection.commit()

		# request.form['authority'] = authority
		#close conn
		cur.close()

		flash('Update successful', 'success')
		# return redirect(url_for('cms.viewusers'))
		return render_template('cms/edituser.html', form=form, status=enabled_new)
	return render_template('cms/edituser.html', form=form)


#Delete user -- this is working
@mod.route('/admin/deleteuser/<string:user_id>', methods=['POST'])
@login_required
@roles_required
def deleteuser(user_id):
	#app.logger.info([user_id])
	
	cur = mysql.connection.cursor()
	#cur.execute("DELETE FROM authorities WHERE user_id=%s", [user_id])
	#cur.execute("SELECT user_id, authority from authorities where user_id=%s", [user_id])
	#auth_table = cur.fetchone()
	#mysql.connection.commit()

	cur.execute("DELETE FROM user WHERE user_id=%s", [user_id])
	mysql.connection.commit()


	
	cur.execute("SELECT user_id from user where user_id = %s", [user_id])
	test = cur.fetchone()
	if test is None:
		flash("User is Deleted", 'success')
		return redirect(url_for('cms.viewusers'))
	else:
		flash("Query is not working", 'danger')
		return redirect(url_for('cms.viewusers'))

	mysql.connection.commit()
	#close conn
	cur.close()
	mysql.connection.close()


# @mod.route('/admin/edituser/<int:user_id>')
# @login_required
# def edituser(user_id):
# 	cur = mysql.connection.cursor()
# 	user_result = cur.execute("SELECT * FROM users_v2 u join authorities a on u.user_id = a.user_id having user_id = %s", ([user_id]))
# 	users_data = cur.fetchone()

# 	if user_result > 0:
# 		return render_template('cms/edituser.html', data=users_data, id=)
# 	else:
# 		msg = 'No user found.'
# 		return render_template('cms/show_users.html', msg=msg)

# 	mysql.connection.commit()
# 	#close conn
# 	cur.close()
# 	mysql.connection.close()


