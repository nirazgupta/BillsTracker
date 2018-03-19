from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DecimalField, DateField, BooleanField

# Resister form
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Password do not match')
		])
	confirm = PasswordField('Confirm Password')



class EditUserForm(Form):
	name = StringField('Name', [validators.Length(min=2, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	authority = StringField('authority', [validators.Length(min=2, max=20)])
	enabled = BooleanField()


# Transaction Entry form
class TransactionForm(Form):
	comment = TextAreaField('comment', [validators.Length(min=3, max=200)])
	#entry_date = DateField('entry_date', format='%m/%d/%Y') 
	#DateField('entry_date', format='%y/%m/%d')
	item = StringField('item', [validators.Length(min=4, max=101)])
	payer = StringField('payer', [validators.Length(min=3, max=51)])
	amount = DecimalField('amount')
	status = StringField('status', [validators.Length(min=1, max=15)])




