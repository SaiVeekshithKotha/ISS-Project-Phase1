from flask import Flask, render_template, redirect, url_for, request, abort, session, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
import pymysql

app = Flask(__name__)
app.secret_key='your_secret_key'
jwt = JWTManager(app)

mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'Veekshith@06'
mysql_db = 'project'



connection = pymysql.connect(host=mysql_host,user=mysql_user,password = mysql_password,db=mysql_db,cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def welcome():
    access_token_cookie = request.cookies.get('access_token_cookie')
    if access_token_cookie:
        try:

    return render_template('index.html')

@app.route('/registration',methods=['GET','POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name=request.form['Name']
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE Username = %s "
            cursor.execute(sql, (username))
            user = cursor.fetchone()
            if user:
                error = 'Invalid, username already exists'
                return render_template('registration.html', error=error)
            else:
                sql1 = """ INSERT INTO Users (Username, Email, Name, Password) VALUES(%s,%s,%s,%s) 
                ;"""
                cursor.execute(sql1, (username,email,name,password))
                connection.commit()
                return redirect(url_for('login'))
            


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Users WHERE Username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            if user:
                # session['user_id'] = user['id']
                # return redirect(url_for('index'))
                return render_template('function.html')
            else:
                error = 'Invalid username or password'
                # return render_template('login.html', error=error)
                return '<h1>User not found.<h1>'
    

@app.route('/function', methods=['GET', 'POST'])
def function():
    return render_template('function.html')

@app.route('/video', methods=['GET', 'POST'])
def video():
    return render_template('video.html')


if __name__ == '__main__':
    app.run(debug=True)