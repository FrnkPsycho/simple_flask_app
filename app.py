from flask import Flask, request, render_template
import sqlite3, os
import hmac, random, re

app = Flask(__name__)


def hmac_sha256(key, s):
    return hmac.new(key.encode('utf-8'), s.encode('utf-8'), 'sha256').hexdigest()


class User(object):

    def __init__(self, username, password):
        self.username = username
        self.key = str([random.randint(48, 122) for x in range(20)])
        self.password = hmac_sha256(self.key, password)


# create database
db = os.path.join(os.path.dirname('__file__'), 'test.db')
if not os.path.isfile(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('create table user(username varchar(20), key varchar(10000), password varchar(10000))')
    #admin user
    admin = User('admin','12345')
    print('admin info:',admin.key,admin.password)
    cursor.execute(r"insert into user(username,key,password) values(?,?,?)",(admin.username,admin.key, admin.password))
    cursor.close()
    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET'])
def login_form():
    return render_template('form.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(r'select * from user where username=?', (username,))
    except IndexError as e:
        print(e,'user not found')
        return render_template('form.html', message='Invaild username', username=username)
    finally:
        value = cursor.fetchall()
        print(value)
        try:
            if value[0][2] == hmac_sha256(value[0][1], password):
                return render_template('accessed.html', username=username)
        except IndexError as e:
            print(e, 'user not found')
            return render_template('form.html', message='Invalid username or password', username=username)
    return render_template('form.html', message='Invalid username or password', username=username)


@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    sec_password = request.form['sec_password']
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute('select username from user where username=?', (username,))
        if cursor.rowcount == -1:
            print('A User tried a valid username to register!')
    except sqlite3.OperationalError as e:
        print('OperationalError:', e)
    finally:
        values = cursor.fetchall()
    if not values:
        if re.match('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password):
            if sec_password == password:
                enc_user = User(username,password)
                cursor.execute('insert into user(username,key,password) values(?,?,?)', (enc_user.username, enc_user.key, enc_user.password))
                print('New User Registered:', enc_user.username, enc_user.key, enc_user.password)
                cursor.close()
                conn.commit()
                conn.close()
            else:
                return render_template('register.html',message='Sorry,the passwords you input twice are not matched!',username=username)
        else:
            return render_template('register.html', message='Sorry,the password is invalid! At least 6 digits,alphabet and numbers are required!',username=username)
        return render_template('form.html', message='Registered sucessfully!',username=username)
    return render_template('register.html', message='Sorry,the username already exit!')


if __name__ == '__main__':
    app.run()
