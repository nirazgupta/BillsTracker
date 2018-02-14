from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DecimalField
from wtforms.fields.html5 import DateField

# Resister form
class RegisterForm(Form):
	fname = StringField('First Name', [validators.DataRequired(),validators.Length(max=50)], render_kw={"placeholder": "First Name"})
	lname = StringField('Last Name', [validators.DataRequired(),validators.Length(max=50)], render_kw={"placeholder": "Last Name"})
	username = StringField('Username', [validators.Length(min=4, max=25)], render_kw={"placeholder": "Username"})
	email = StringField('Email', [validators.Length(min=6, max=50), validators.Email(message=None)], render_kw={"placeholder": "abc@gmail.com"})
	password = PasswordField('Password', [validators.DataRequired(),
			validators.EqualTo('confirm', message='Password do not match')], render_kw={"placeholder": "Password"})
	confirm = PasswordField('Confirm Password', render_kw={"placeholder": "Retype the password"})



# Transaction Entry form
# class TransactionForm(Form):
# 	comment = TextAreaField('Comment', [validators.Length(min=0, max=200)])
# 	#entry_date = DateField('Date', format='%m/%d/%Y') 
# 	#DateField('entry_date', format='%y/%m/%d')
# 	item = StringField('Item', [validators.Length(min=4, max=101)])
# 	payer = StringField('Paid by', [validators.Length(min=3, max=51)])
# 	amount = DecimalField('Amount', places=2)
# 	status = StringField('Status', [validators.Length(min=1, max=15)])

class TransactionForm(Form):
	comment = StringField('Comment', render_kw={"placeholder": "Enter a comment, if any!"})
	manual_date = DateField('Date', format='%Y-%m-%d') 
	#DateField('entry_date', format='%y/%m/%d')
	item = StringField('Item', [validators.DataRequired(),validators.Length(min=3, max=50)], render_kw={"placeholder": "Name of Item or Activity"})
	payer = StringField('Paid by', [validators.DataRequired()], render_kw={"placeholder": "Name of the payer"})
	amount = DecimalField('Amount', places=2, render_kw={"placeholder": "Enter the amount"})
	status = StringField('Status', [validators.DataRequired()], render_kw={"placeholder": "Enter 'new' for status "})

class EditTransForm(Form):
	comment = StringField('Comment')
	manual_date = DateField('Date', format='%Y-%m-%d') 
	#DateField('entry_date', format='%y/%m/%d')
	item = StringField('Item', [validators.DataRequired(),validators.Length(min=3, max=50)])
	payer = StringField('Paid by', [validators.DataRequired()])
	amount = DecimalField('Amount', places=2)
	status = StringField('Status', [validators.DataRequired()])


class EmailForm(Form):
	email = StringField('Email', [validators.DataRequired(), validators.Email(message=None)], render_kw={"placeholder": "abc@gmail.com"})

class PasswordForm(Form):
    password = PasswordField('New Password', [
    	validators.DataRequired(),
    	validators.EqualTo('confirm', message='Password do not match')
    	])
    confirm = PasswordField('Confirm Password')