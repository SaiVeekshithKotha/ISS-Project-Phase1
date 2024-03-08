from flask import Flask, render_template, redirect, url_for, request, abort, session, make_response,jsonify,send_file
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
# import json
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
# from datetime import timedelta
from io import BytesIO
from PIL import Image
import base64
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'Veekshith@06'
mysql_db = 'project_database'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)

connection = pymysql.connect(host=mysql_host,user=mysql_user,password = mysql_password,db=mysql_db,cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def welcome():
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
            if user is not None:
                retrieve_password = user['Password']
                if check_password_hash(retrieve_password,password):
                     return render_template('function.html',userName=username)
                else:
                    error = "Invalid username or password."
                    return render_template('login.html', error=error)
            else:
                error = "Username doesn't exist."
                return render_template('login.html', error=error)
    return render_template('login.html')   
    

@app.route('/upload',methods = ['POST'])
def upload():
    
    try:
        images = request.files.getlist('images')
        username = request.form['username']
        print("username:",username)
        print("img:",images)


        with connection.cursor() as cursor: 
            create_image_table = '''CREATE TABLE IF NOT EXISTS Images (
            Image_Id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            Username VARCHAR(255) NOT NULL,
            Image_name VARCHAR(255) NOT NULL,
            Filetype VARCHAR(100) NOT NULL,
            Img LONGBLOB
            );'''

            cursor.execute(create_image_table)
            
        
            for image in images:

                if image.filename and allowed_file(image.filename):
                    cursor.execute("SELECT * FROM Images WHERE Username = %s and Image_name = %s",(username,image.filename))
                    existing_image = cursor.fetchall()
                    if existing_image:
                        return jsonify({'error':f'file {image.filename} already exists.'}),400
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'],image.filename)
                    image.save(filepath)
                    with open(filepath,"rb") as f:
                        image_blob = f.read()
                    
                    insert_image_query = "INSERT INTO Images(Username,Image_name,Filetype,Img) VALUES(%s,%s,%s,%s)"
                    cursor.execute(insert_image_query,(username,image.filename,image.content_type,image_blob))
            connection.commit()

            return jsonify({'message':'Images uploaded successfully.'}),200
    except Exception as e:
        print('Error uploading images:', e)
        return jsonify({'message': 'Error uploading images. Please try again.'}), 400
    
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
def allowed_file(Filename):
    print("hello")

    return '.' in Filename and Filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/display', methods=['GET'])
def display():
    username = request.args.get('username')
    print("Received username:", username)

    with connection.cursor() as cursor:
        sql = "SELECT Img, Filetype FROM Images WHERE username = %s"
        cursor.execute(sql, (username,))
        results = cursor.fetchall()

        if not results:
            return jsonify({'error': 'User not found in the database.'}), 404

        images_data = [{'format': result['Filetype'].split('/')[1].lower(), 'data': base64.b64encode(result.get('Img')).decode('utf-8')} for result in results]

        if not images_data:
            return jsonify({'error': 'Image data not found in the database.'}), 404

        return jsonify({'images': images_data})




@app.route('/function/<userName>', methods=['GET', 'POST'])
def function(userName):
    return render_template('function.html',userName=userName)

@app.route('/video', methods=['GET', 'POST'])
def video():
        return render_template('video.html')

@app.route('/get_audio_from_database')
def get_all_audio():
    try:
        # Connect to the database
        connection = pymysql.connect(host=mysql_host,user=mysql_user,password = mysql_password,db=mysql_db,cursorclass=pymysql.cursors.DictCursor)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT Audio_id FROM Audio")
            id = [f['Audio_id'] for f in cursor.fetchall()]

            return jsonify({'id':id})
    except Exception as ex: 
        return jsonify({"Error": f'{ex} has occured.'})


@app.route('/audio/<id>')
def serve_audio(id):

    connection = pymysql.connect(host=mysql_host,user=mysql_user,password = mysql_password,db=mysql_db,cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        try:
            query = "SELECT AudioData FROM Audio WHERE Audio_id = %s"
            cursor.execute(query, (id))
            audio_data = cursor.fetchone()['AudioData']
            if audio_data:
                return send_file(BytesIO(audio_data), mimetype='audio/mp3')
            else: 
                return jsonify({'Error': 'Audio file was not found.'}), 404
        except Exception as e:
            return jsonify({'Error':f'{e} as occured.'}), 404


@app.route('/show_images', methods=['GET'])
def show_images():
    selected_images = request.args.getlist('image')

    return render_template('video.html', selected_images=selected_images)

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('welcome')))
    response.set_cookie('access_token_cookie', '', expires=0)  
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)