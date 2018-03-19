from flask_script import Manager
from it680vizapp import app
from passlib.hash import sha256_crypt

from it680vizapp import mysql

manager = Manager(app)

@manager.command
def drop():
    cur = mysql.connection.cursor()
    drop = '''
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS user;
            DROP TABLE IF EXISTS user_transaction;
            DROP TABLE IF EXISTS transaction;
            DROP TABLE IF EXISTS tbl_group;
            DROP TABLE IF EXISTS user_group;
            SET FOREIGN_KEY_CHECKS = 1;
    '''
    cur.execute(drop)
    #mysql.connection.commit()
    cur.close()

@manager.command
def create_tables():

    cur = mysql.connection.cursor()

    user = '''
            CREATE TABLE IF NOT EXISTS user (
            user_id INT(11) NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) NULL DEFAULT NULL,
            email VARCHAR(50) NULL DEFAULT NULL,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(200) NOT NULL,
            register_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            enabled TINYINT(1) NULL DEFAULT NULL,
            fname VARCHAR(50) NULL DEFAULT NULL,
            lname VARCHAR(50) NULL DEFAULT NULL,
            super_user boolean not null default 0,
            PRIMARY KEY (user_id));
            '''

    groups = '''
                CREATE TABLE IF NOT EXISTS tbl_group (
                group_id INT(11) NOT NULL AUTO_INCREMENT,
                group_name VARCHAR(50) NOT NULL,
                grp_created_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id),
                UNIQUE INDEX ix_group_username (group_id ASC));

    '''

    user_groups = '''
                CREATE TABLE IF NOT EXISTS user_group (
                user_group_id INT(11) NOT NULL AUTO_INCREMENT,
                group_id INT(11) NOT NULL,
                user_id INT(11) NOT NULL,
                group_admin boolean not null default 0,
                PRIMARY KEY (user_group_id),
                UNIQUE INDEX ix_group_username (user_id ASC, group_id ASC),
                CONSTRAINT fk1_group_users FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk2_group_users FOREIGN KEY (group_id) REFERENCES tbl_group (group_id) ON DELETE CASCADE ON UPDATE CASCADE);

                    '''

    transaction = '''
                CREATE TABLE IF NOT EXISTS transaction (
                transaction_id INT(11) NOT NULL AUTO_INCREMENT,
                user_group_id INT(11) NOT NULL,
                entry_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                comment VARCHAR(150) NULL DEFAULT NULL,
                item VARCHAR(100) NULL DEFAULT NULL,
                payer VARCHAR(50) NULL DEFAULT NULL,
                amount DECIMAL(10,2) NULL DEFAULT NULL,
                status VARCHAR(15) NULL DEFAULT NULL,
                manual_date DATE NULL DEFAULT NULL,
                PRIMARY KEY (transaction_id),
                CONSTRAINT group_transaction_ibfk_2 FOREIGN KEY (user_group_id) REFERENCES user_group (user_group_id) ON DELETE CASCADE ON UPDATE CASCADE);
    '''

    user_transaction = '''
                        CREATE TABLE IF NOT EXISTS user_transaction (
                        user_id INT(11) NOT NULL,
                        transaction_id INT(11) NOT NULL,
                        share_amount DECIMAL(10,2) NOT NULL,
                        amt_lent DECIMAL(10,2) NULL DEFAULT NULL,
                        per_share DECIMAL(10,2) NULL DEFAULT NULL,
                        PRIMARY KEY (user_id, transaction_id),
                        INDEX fk_tran_id(transaction_id ASC),
                        CONSTRAINT user_transaction_ibfk_1 FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        CONSTRAINT user_transaction_ibfk_2 FOREIGN KEY (transaction_id) REFERENCES transaction (transaction_id) ON DELETE CASCADE ON UPDATE CASCADE);

                    '''
    
    cur.execute(user)
    cur.execute(groups)
    cur.execute(user_groups)
    cur.execute(transaction)
    cur.execute(user_transaction)
    
    mysql.connection.commit()
    cur.close()

@manager.command
def create_admin():
    cur = mysql.connection.cursor()
    create_admin='''INSERT INTO user (name, email, username, password, enabled, super_user)
										 VALUES(%s, %s, %s, %s, %s, %s)''' 
    name = input("Enter name: " )
    email = input("Enter email: ")
    username = input("Enter username: ")
    _password = input("Password: ")
    password = sha256_crypt.encrypt(_password)
    enabled = True
    super_user = True
    cur.execute(create_admin, (name, email, username, password, enabled, super_user))
    mysql.connection.commit()
    cur.close()

app.jinja_env.auto_reload = True

app.config["CACHE_TYPE"] = "null"

#cache.init_app(app)
app.config['TEMPLATES_AUTO_RELOAD']=True

if __name__ == '__main__':
	manager.run() 