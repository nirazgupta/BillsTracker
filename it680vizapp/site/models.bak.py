from it680vizapp import app
from it680vizapp import mysql

from manage.py import manager


from flask_mysqldb import MySQL
mysql = MySQL(app)


@manager.command
def drop():
    cur = mysql.connection.cursor()
    drop = '''
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS authorities;
            DROP TABLE IF EXISTS users_v2;
            DROP TABLE IF EXISTS user_transaction;
            DROP TABLE IF EXISTS transaction;
            SET FOREIGN_KEY_CHECKS = 1;
    '''
    cur.execute(drop)
    mysql.connection.commit()
    cur.close()

@manager.command
def create_tables():

    cur = mysql.connection.cursor()

    user = '''
            CREATE TABLE IF NOT EXISTS users_v2 (
            user_id INT(11) NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) NULL DEFAULT NULL,
            email VARCHAR(50) NULL DEFAULT NULL,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(200) NOT NULL,
            register_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            enabled TINYINT(1) NULL DEFAULT NULL,
            fname VARCHAR(50) NULL DEFAULT NULL,
            lname VARCHAR(50) NULL DEFAULT NULL,
            PRIMARY KEY (user_id))
            '''

    authorities = '''
                    CREATE TABLE IF NOT EXISTS authorities(
                    auth_id INT(11) NOT NULL AUTO_INCREMENT,
                    authority VARCHAR(50) NOT NULL,
                    user_id INT(11) NOT NULL,
                    PRIMARY KEY (auth_id),
                    UNIQUE INDEX ix_auth_username (user_id ASC, authority ASC),
                    CONSTRAINT fk_authorities_users
                    FOREIGN KEY (user_id)
                    REFERENCES it680vizapp.users_v2 (user_id))
                    ENGINE = InnoDB
                    AUTO_INCREMENT = 26
                    DEFAULT CHARACTER SET = utf8
                    '''

    transaction = '''
                CREATE TABLE IF NOT EXISTS transaction (
                id INT(11) NOT NULL AUTO_INCREMENT,
                entry_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                comment VARCHAR(150) NULL DEFAULT NULL,
                item VARCHAR(100) NULL DEFAULT NULL,
                payer VARCHAR(50) NULL DEFAULT NULL,
                amount DECIMAL(10,2) NULL DEFAULT NULL,
                status VARCHAR(15) NULL DEFAULT NULL,
                user_id INT(11) NULL DEFAULT NULL,
                manual_date DATE NULL DEFAULT NULL,
                amount_lent DECIMAL(10,2) NULL DEFAULT NULL,
                PRIMARY KEY (id))
                ENGINE = InnoDB
                DEFAULT CHARACTER SET = utf8
    '''

    user_transaction = '''
                        CREATE TABLE IF NOT EXISTS user_transaction (
                        user_id INT(11) NOT NULL,
                        id INT(11) NOT NULL,
                        share_amount DECIMAL(10,2) NOT NULL,
                        amt_lent DECIMAL(10,2) NULL DEFAULT NULL,
                        per_share DECIMAL(10,2) NULL DEFAULT NULL,
                        PRIMARY KEY (user_id, id),
                        INDEX fk_tran_id(id ASC),
                        CONSTRAINT user_transaction_ibfk_1
                            FOREIGN KEY (user_id)
                            REFERENCES users_v2 (user_id)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE,
                        CONSTRAINT user_transaction_ibfk_2
                            FOREIGN KEY (id)
                            REFERENCES transaction (id)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE)
                        ENGINE = InnoDB
                        DEFAULT CHARACTER SET = utf8
                    '''
    cur.execute(authorities)
    cur.execute(user)
    cur.execute(transaction)
    cur.execute(user_transaction)
    
    mysql.connection.commit()
    cur.close()
