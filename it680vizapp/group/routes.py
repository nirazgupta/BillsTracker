from flask import Flask, Blueprint, jsonify
from flask import Flask, render_template, flash, redirect, url_for, g, session, logging, request
from passlib.hash import sha256_crypt
from functools import wraps
from sqlalchemy.orm import sessionmaker
from jinja2 import Environment, PackageLoader, select_autoescape
from it680vizapp import mysql, mail, serialize
from flask_mail import Message
from collections import Counter
#from mysql import escape_string as thwart
from flask import current_app
from flask_paginate import Pagination, get_page_parameter
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
import pandas as pd
import json
#from wapy.api import Wapy
#from walmart_api_client import WalmartApiClient
import pandas.io.sql as psql

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

#Site blue print
mod = Blueprint('group', __name__, template_folder='templates', static_url_path='/group/static', static_folder='./static')
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

##function to get user_info or group_info based on arguments
def query_user(arg, type):
	cur = mysql.connection.cursor()

	if type == 'get_user':
		query_trans = ''' select u.user_id, tg.group_name, u.name, ug.group_admin, ug.group_id
							from user_group ug
							join tbl_group tg on ug.group_id = tg.group_id
							join user u on u.user_id = ug.user_id
							where u.user_id=%s
						'''
		cur.execute(query_trans, ([arg]))
		result = cur.fetchall()
		mysql.connection.commit()
		cur.close()
		return result
	elif type == 'get_owner_group':
		search_query = """
						select u.name, ug.group_id, tg.group_name, ug.group_admin
						from user_group ug join tbl_group tg
						on tg.group_id = ug.group_id
						join user u on u.user_id = ug.user_id
						where tg.group_name LIKE %s and ug.group_admin=%s
						"""
		cur.execute(search_query, ([arg], 1))
		result = cur.fetchall()
		mysql.connection.commit()
		cur.close()
		return result
	
	

def get_users_id(arg):
	cur = mysql.connection.cursor()
	query = '''
				select user_id, email, name from user where username=%s
			'''
	cur.execute(query, ([arg]))
	user_data = cur.fetchone()
	mysql.connection.commit()
	cur.close()
	return user_data

##function to check if user already exist in the group
def check_user_in_group(arg1, arg2):
	cur = mysql.connection.cursor()
	query = '''
				select group_id from user_group where user_id=%s and group_id=%s
			'''
	cur.execute(query, ([arg1], [arg2]))
	user_data = cur.fetchall()
	mysql.connection.commit()
	current_app.logger.info(user_data)
	cur.close()
	return user_data

@mod.route('/create_group', methods = ['GET','POST'])
@login_required
@register_breadcrumb(mod, '.dashboard', 'Dashboard', order=4)
def create_group():
	if request.method == 'POST':
		grp_name = request.form['group_name']
		cur = mysql.connection.cursor()

		usr_data = get_users_id(session['username'])
		user_id = usr_data['user_id'] 

		existing_query_group = '''
							select group_name from tbl_group where group_name=%s
						'''
		cur.execute(existing_query_group, ([grp_name]))			
		existing_group = cur.fetchone()

		if existing_group is None:
			creation_query = '''
							INSERT INTO tbl_group (group_name) VALUES(%s)
							''' 
			cur.execute(creation_query, ([grp_name]))
			mysql.connection.commit()

			get_grp_id = '''
						select group_id from tbl_group where group_name=%s
						'''
			cur.execute(get_grp_id, ([grp_name]))
			_grp_id = cur.fetchone()

			fetched_group_id = _grp_id['group_id']

			
			user_group_owner_insert = '''
								insert into user_group (group_id, user_id) values(%s, %s)
								'''
			cur.execute(user_group_owner_insert, (fetched_group_id, user_id))
			mysql.connection.commit()

			update_group_admin = '''
								update user_group set group_admin=%s where user_id=%s and group_id=%s
								'''
			cur.execute(update_group_admin, (1,user_id, fetched_group_id))
			mysql.connection.commit()
		else:
			error = 'Group already exists.'
			return render_template('site/group/create_group.html', error=error)
	return render_template('site/group/create_group.html')



# @mod.route('/_show_group', methods=['GET'])
# @login_required
# @register_breadcrumb(mod, '.dashboard', 'Dashboard', order=4)
# def _show_group():
# 	if request.method == 'GET':
# 		user = session['username']

# 		usr_data = get_users_id([user])
# 		usr_id = usr_data['user_id']

# 		result = query_user(usr_id, 'get_user')
# 		#json_data = jsonify(result)
# 		return jsonify(result)

@mod.route('/show_group', methods=['GET'])
@login_required
@register_breadcrumb(mod, '.dashboard', 'Dashboard', order=4)
def show_group():
	if request.method == 'GET':
		user = session['username']

		usr_data = get_users_id([user])
		usr_id = usr_data['user_id']

		result = query_user(usr_id, 'get_user')

		return jsonify(result)


def get_grp_result(group_id, type):
	cur = mysql.connection.cursor()
	if type=='get_users':
		query = '''select distinct u.name, ug.group_id
				from user_group ug join user u on u.user_id = ug.user_id 
				where ug.group_id=%s'''
		cur.execute(query,([group_id]))
		result = cur.fetchall()
		return result
	else:
		query = '''select group_name
				from tbl_group
				where group_id=%s'''
		cur.execute(query,([group_id]))
		result = cur.fetchall()
		return result

@mod.route('/transactions/<string:group_id>', methods=['GET', 'POST'])
@login_required
def transactions(group_id):
	session['group_id'] = group_id
	grp_result = get_grp_result(group_id,'get_users')
	group_name = get_grp_result(group_id,'')
	group_trans = tran_view()
	group_total = group_trans_details()
	user_group_total = user_trans_details()
	user_expense = get_expense_bal2()

	current_app.logger.info(user_expense)
	data = {"group_people":grp_result, "trans":group_trans, "group":group_name, "group_total":group_total, 
			"user_group_total":user_group_total}

	if group_trans is not None:
		return render_template('site/transactions.html', data=data, user_expense=user_expense)
	else:
		msg = 'No records found.'
		return render_template('site/transactions.html', msg=msg)


def tran_view():
	user = session['username']
	group_id = session['group_id']
	cur = mysql.connection.cursor()
	query = """SELECT Distinct t.transaction_id, t.item, t.manual_date,
	 			t.amount, t.you_lent, t.your_share, u.name, 
				t.status FROM transaction t
				join user u on u.user_id = t.user_id
				where t.group_id=%s order by t.status desc, t.manual_date
				"""
	result = cur.execute(query, ([group_id]))
	data = cur.fetchall()
	return data

def group_trans_details():
	group_id = session['group_id']
	cur = mysql.connection.cursor()
	query = """
			select sum(amount) as total
			from transaction t 
			where group_id=%s and t.status='unpaid'
			"""
	cur.execute(query, ([group_id]))
	
	data = cur.fetchall()
	
	return data

def user_trans_details():
	user = session['username']
	group_id = session['group_id']
	user = session['username']

	usr_data = get_users_id([user])
	usr_id = usr_data['user_id']

	cur = mysql.connection.cursor()
	query = """
			select sum(amount) as total, sum(you_lent) as lent
			from transaction t 
			where group_id=%s and user_id=%s and t.status='unpaid'
			"""
	cur.execute(query, (group_id, usr_id))
	data = cur.fetchall()
	return data

def get_expense_bal2():
	user = session['username']
	group_id = session['group_id']
	user = session['username']

	usr_data = get_users_id([user])
	usr_id = usr_data['user_id']
	
	cur = mysql.connection.cursor()
	query = """
			select sum(share_amount) as shr_amount 
			from user_transaction ut join transaction t 
			on t.transaction_id = ut.transaction_id
			where ut.user_id=%s and group_id=%s and t.status='unpaid'
			"""
	cur.execute(query, ([usr_id, group_id]))
	data=cur.fetchone()
	return data


@mod.route('/owings/<string:transaction_id>', methods=['GET', 'POST'])
@login_required
def owed_users(transaction_id):
	cur = mysql.connection.cursor()
	user = session['username']

	usr_data = get_users_id([user])
	usr_id = usr_data['user_id']

	query = """SELECT ut.user_id, u.name, ut.transaction_id, ut.share_amount
				from user_transaction ut join user u 
				on u.user_id = ut.user_id
				where ut.transaction_id=%s AND ut.user_id NOT IN (select user_id from transaction where transaction_id =%s)
				"""
		
	cur.execute(query, ([transaction_id], [transaction_id]))
	data = cur.fetchall()
	#converted=Convert(data, dic)
	return jsonify(data)



@mod.route('/joingroup', methods=['GET', 'POST'])
@login_required
def joingroup():
	if request.method == 'POST':
		search = request.form['search_group']
		result = query_user((["%"+search+"%"]), 'get_owner_group')
		current_app.logger.info(result)
		return render_template('site/group/add_to_group.html', data=result)
	return render_template('site/group/add_to_group.html')


@mod.route('/add_to_the_group', methods=['GET', 'POST'])
@login_required
def add_to_the_group():
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		grp_id = request.form['group_id']

		user = session['username']

		usr_data = get_users_id([user])
		usr_id = usr_data['user_id']

		if_usr_in_grp = check_user_in_group(usr_id, grp_id)
	
		if if_usr_in_grp:
			flash('You have already joined this group', 'danger')
			return redirect(url_for('group.joingroup'))
		else:
			add_user_to_group = """
								insert into user_group (group_id, user_id) values(%s, %s)
								"""
			cur.execute(add_user_to_group, (grp_id, usr_id))
			mysql.connection.commit()
			flash('Welcome to the group', 'success')
			return redirect(url_for('group.joingroup'))
	return render_template('site/group/add_to_group.html')




@mod.route('/leave_group/<string:group_id>', methods=['GET', 'POST'])
@login_required
def leave_group(group_id):
	cur = mysql.connection.cursor()

	user = session['username']

	usr_data = get_users_id([user])
	usr_id = usr_data['user_id']

	check_balance = """
							select DISTINCT sum(t.amount) as t_amount, sum(ut.share_amount) as ut_share
							from transaction t join user_transaction ut 
							on ut.transaction_id=t.transaction_id
							where ut.user_id=%s and t.status = 'unpaid' and t.group_id=%s
							"""
	cur.execute(check_balance, ([usr_id, group_id]))

	result = cur.fetchone()

	get_transaction_id = """
							select transaction_id 
							from transaction 
							where group_id = %s and user_id =%s
							"""
	cur.execute(get_transaction_id, ([group_id, usr_id]))
	result2 = cur.fetchall()

	get_user_transaction_id = """
							select *
							from user_transaction 
							where group_id = %s and user_id =%s
							"""
	cur.execute(get_transaction_id, ([group_id, usr_id]))
	result3 = cur.fetchall()

	t_amount = result['t_amount']
	ut_share = result['ut_share']


	if ut_share is not None:
		flash('You have pending balance in the group.' +'   ' + '$' +str(ut_share), 'success')
		current_app.logger.info(result3)
	elif result2 and result3:
		
		try:
			transaction_id = []
			for i in result2:
				transaction_id.append(i['transaction_id'])
	
			del_from_user_transaction = '''
									DELETE FROM USER_TRANSACTION
									where transaction_id=%s and user_id=%s
									'''
			cur.execute(del_from_user_transaction, ([transaction_id, usr_id]))
			mysql.connection.commit()

			del_from_transaction = '''
									DELETE FROM TRANSACTION
									where group_id=%s and user_id=%s
									'''
			cur.execute(del_from_transaction, ([group_id, usr_id]))
			mysql.connection.commit()

			del_from_user_group = '''
								DELETE FROM USER_GROUP
								WHERE GROUP_ID=%s and USER_ID=%s
								'''
			cur.execute(del_from_user_group, ([group_id, usr_id]))
			mysql.connection.commit()


			check_users_in_grp = '''
										select user_id
										from user_group
										where group_id = %s
									'''
			cur.execute(check_users_in_grp, ([group_id]))
			user_fetch_result = cur.fetchall()
				

			if not user_fetch_result:
				cur = mysql.connection.cursor()
				del_group = '''
							DELETE FROM tbl_group
							where group_id=%s
								'''
				cur.execute(del_group, ([group_id]))
				mysql.connection.commit()
				# flash('You have successfully left the group.')

		except mysql.connection.Error as err:
			print("Something went wrong: {}".format(err))
			mysql.connection.rollback()
			cur.close()

	else:

		del_from_user_group = '''
								DELETE FROM USER_GROUP
								WHERE GROUP_ID=%s and USER_ID=%s
								'''
		cur.execute(del_from_user_group, ([group_id, usr_id]))
		mysql.connection.commit()


		check_users_in_grp = '''
									select user_id
									from user_group
									where group_id = %s
								'''
		cur.execute(check_users_in_grp, ([group_id]))
		user_fetch_result = cur.fetchall()
			

		if not user_fetch_result:
			cur = mysql.connection.cursor()
			del_group = '''
						DELETE FROM tbl_group
						where group_id=%s
							'''
			cur.execute(del_group, ([group_id]))
			mysql.connection.commit()
			flash('You have successfully left the group.', 'success')
			return redirect(url_for('site.dashboard'))
		# flash('there is no record')
	return redirect(url_for('site.dashboard'))
