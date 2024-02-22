from flask import Flask, render_template, redirect, url_for, request, abort, session, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
import json
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from datetime import timedelta

app = Flask(__name__)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_COOKIE_SECURE'] = False 
app.secret_key = 'your_secret_key_here'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/function'
# app.config['JWT_REFRESH_COOKIE_PATH'] = '/login'
jwt = JWTManager(app)

mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'Veekshith@06'
mysql_db = 'project_database'



connection = pymysql.connect(host=mysql_host,user=mysql_user,password = mysql_password,db=mysql_db,cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def welcome():
    access_token_cookie = request.cookies.get('access_token_cookie')
    if access_token_cookie:
        try:
            decoded = decode_token(access_token_cookie)
            userName = decoded.get('sub')
            return redirect(url_for('function', userName=userName))
        except Exception as e:
            print('Error, decoding token:',e)
    return render_template('index.html')

@app.route('/registration',methods=['GET','POST'])
def registration():
    # access_token_cookie = request.cookies.get('access_token_cookie')
    # if access_token_cookie:
    #     try:
    #         decoded = decode_token(access_token_cookie)
    #         userName = decoded.get('sub')
    #         return redirect(url_for('function',userName = userName))
    #     except Exception as e:
    #          print('Error decoding token:',e)

    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name=request.form['Name']
        hash_password = generate_password_hash(password,method='pbkdf2:sha256')
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Users WHERE Username = %s AND  Email = %s"
            cursor.execute(sql, (username,email))
            user = cursor.fetchone()
            if user:
                error = 'Invalid, username or email already exists'
                return render_template('registration.html', error=error)
            else:
                sql1 = """ INSERT INTO Users (Username, Email, Name, Password) VALUES(%s,%s,%s,%s) 
                ;"""
                cursor.execute(sql1, (username,email,name,hash_password))
                connection.commit()
                return redirect(url_for('login'))
            


@app.route('/login', methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Users WHERE Username = %s"
            cursor.execute(sql, (username))
            user = cursor.fetchone()
            retrieve_password = user['Password']
            if user and check_password_hash(retrieve_password,password):
                # return redirect(url_for('index'))
                # access_token = create_access_token(identity=username)
                access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))
                response = make_response(redirect(url_for('function', userName=username)))
                response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True)
                return response
                # return render_template('function.html',userName=username)
            else:
                error = 'Invalid username or password'
                return render_template('login.html', error=error)
                # return '<h1>User not found.<h1>'

    return render_template('login.html')   
    

@app.route('/function/<userName>', methods=['GET', 'POST'])
@jwt_required()
def function(userName):
    currentUser = get_jwt_identity()
    if currentUser != userName:
        print("Error: Current user does not match requested user.")
        abort(403)  # Returns a forbidden error i.e., (HTTP status code 403)
    return render_template('function.html',userName=userName)

@app.route('/video', methods=['GET', 'POST'])
def video():
    return render_template('video.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('welcome')))
    response.set_cookie('access_token_cookie', '', expires=0)  # Clearing the access token cookie
    return response

if __name__ == '__main__':
    app.run(debug=True)