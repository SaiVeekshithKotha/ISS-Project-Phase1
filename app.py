from flask import Flask, render_template, redirect, url_for, request, abort, session, make_response,jsonify,send_from_directory,after_this_request,send_file
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
# import json
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
# from datetime import timedelta
from io import BytesIO
from PIL import Image
import base64
import os
import numpy as np
from moviepy.editor import ImageSequenceClip, concatenate_audioclips, AudioFileClip
# from urllib.request import urlopen
import tempfile

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_here'
jwt = JWTManager(app)

mysql_host = 'localhost'
mysql_user = 'Saicharan30'
mysql_password = 'Saicharan@123'
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
                    access_token = create_access_token(identity=username)
                    print(access_token)
                    session['token'] = access_token
                    session['username'] = username
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
        # username = request.form['username']
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not logged in'}), 401
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
    # username = request.args.get('username')
    username = session.get('username')
    if not username:
        return jsonify({'error': 'User not logged in'}), 401
    print("Received username:", username)

    with connection.cursor() as cursor:
        sql = "SELECT Image_name, Img, Filetype FROM Images WHERE username = %s"
        cursor.execute(sql, (username,))
        results = cursor.fetchall()

        if not results:
            return jsonify({'error': 'User not found in the database.'}), 404

        images_data = [{'filename': result['Image_name'], 'format': result['Filetype'].split('/')[1].lower(), 'data': base64.b64encode(result.get('Img')).decode('utf-8')} for result in results]

        if not images_data:
            return jsonify({'error': 'Image data not found in the database.'}), 404

        return jsonify({'images': images_data})


@app.route('/function/<userName>', methods=['GET', 'POST'])
def function(userName):
    return render_template('function.html',userName=userName)

@app.route('/back_to_home',methods=['GET'])
def  back_to_home():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'User not logged in'}), 401
    else:
        return render_template('function.html',userName=username)


@app.route('/video', methods=['GET', 'POST'])
def video():
        userName = session.get('username')
        return render_template('video.html',userName = userName)

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
        


# @app.route('/create_video', methods=['GET' , 'POST'])
# def create_video():
#     selected_images_urls = request.form.getlist('selectedImagesURLs[]')
#     selected_audio_ids = request.form.getlist('selectedAudioFilesIds[]')
#     print(selected_images_urls)
#     print(selected_audio_ids)
#     with connection.cursor() as cursor:
#         audio_blobs = []
#         for id in selected_audio_ids:
#             sql = '''SELECT AudioData FROM Audio WHERE Audio_id = %s '''
#             cursor.execute(sql,(id))
#             audio_data = cursor.fetchone()['AudioData']
#             audio_blobs.append(BytesIO())

        
#         image_files = []
#         for url in selected_images_urls:
#         #     response = requests.get(url,stream=True)
#         #     if response.status_code == 200:
#             with urlopen(url) as response:
#                 image_data = response.read()
#                 # Open the image from the response content
#                 img = Image.open(BytesIO(image_data))
#                 # Append the image object to the list
#                 image_files.append(img)
#             # else:
#             #     print(f"Failed to retrieve image from {url}")
        
#         image_arrays = [np.array(img) for img in image_files]

#         # Create a video clip from the sequence of images
#         clip = ImageSequenceClip(image_arrays, fps=30)

#         # Define the output video filename
#         output_video_filename = 'output_video.mp4'

#         # Write the video clip to a file
#         clip.write_videofile(output_video_filename, fps=30)

#         print("Video created successfully:", output_video_filename)
                    


    
#     return jsonify({'messsage':'HI'})
        
@app.route('/create_video', methods=['GET' , 'POST'])
def create_video():
    selected_images_blobs = request.form.getlist('selectedImagesBlobs[]')
    selected_audio_ids = request.form.getlist('selectedAudioFilesIds[]')
    # print(selected_images_blobs)
    print(selected_audio_ids)

    audio_clips= []
    with connection.cursor() as cursor:
        audio_blobs = []
        for id in selected_audio_ids:
            sql = '''SELECT AudioData FROM Audio WHERE Audio_id = %s '''
            cursor.execute(sql,(id))
            audio_data = cursor.fetchone()['AudioData']
            audio_blobs.append(BytesIO(audio_data))
            # audio_clip = AudioFileClip(BytesIO(audio_data))
            # audio_clips.append(audio_clip)
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio_file:
                temp_audio_file.write(audio_data)
                temp_audio_file_name = temp_audio_file.name
            
            audio_clip = AudioFileClip(temp_audio_file_name)
            audio_clips.append(audio_clip)
        
    image_files = []
    for img_base64 in selected_images_blobs:
        try:
            img_data = base64.b64decode(img_base64)
            img = Image.open(BytesIO(img_data))
            image_files.append(img)
        except Exception as e:
            print(f"Error fetching image from : {e}")
    
    # image_arrays = [np.array(img) for img in image_files]
    image_arrays_resized = []
    for img in image_files:
        print("q")
        resized_img =img.resize((640, 480))
        if resized_img.mode == 'RGBA':
            resized_img = resized_img.convert('RGB')
        image_arrays_resized.append(np.array(resized_img))
        print(resized_img.size)
    for x in image_arrays_resized:
        print(x.shape)
    
    # sizes = set(img.size for img in image_arrays_resized)
    # if len(sizes) > 1:
    #     print("Error: Not all images have the same size")
    # Create a video clip from the sequence of images
    num_frames = len(image_arrays_resized)
    fps = 30
    duration_per_frame = 5
    durations = [duration_per_frame] * num_frames    
    video_clip = ImageSequenceClip(image_arrays_resized,durations=durations)
    
    if len(audio_clips) > 1:
        audio_clip = concatenate_audioclips(audio_clips)
    elif len(audio_clips) == 1:
        audio_clip = audio_clips[0]
    else:
        audio_clip = None

    # Set audio duration equal to video duration
    if audio_clip:
        audio_duration = video_clip.duration
        audio_clip = audio_clip.set_duration(audio_duration)

    # Add audio to video clip
    if audio_clip:
        video_clip = video_clip.set_audio(audio_clip)

    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        output_video_filename = temp_file.name
        video_clip.write_videofile(output_video_filename, codec='libx264', fps=fps)
    
    with open(output_video_filename, 'rb') as file:
        video_blob = file.read()
    
    os.remove(output_video_filename)
    
    video_base64 = base64.b64encode(video_blob).decode('utf-8')
    response_data = {
        'video_base64': video_base64,
        'mime_type': 'video/mp4'  # Adjust the MIME type as needed
    }
    return jsonify(response_data)
    # Delete the temporary file
    
    
    # return send_file(BytesIO(video_blob), mimetype='video/mp4', as_attachment=True,download_name='output_video.mp4')

@app.route('/logout')
def logout():
     session.pop('token', None)
     session.pop('username',None)
     return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
