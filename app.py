from flask import Flask, render_template, redirect, url_for, request, abort, session, make_response,jsonify,send_file
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
# import json
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from io import BytesIO
from PIL import Image
import base64
import os
import numpy as np
import cv2
from moviepy.editor import CompositeVideoClip,ImageClip,ImageSequenceClip,concatenate_videoclips, concatenate_audioclips, AudioFileClip,ColorClip
from moviepy.video.fx.resize import resize
import tempfile 


os.environ["DATABASE_URL"] = "postgresql://sai:4CZqNZiXY9EDW6roLqvfKw@saiveekshith-8943.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/project_database?sslmode=verify-full"


app = Flask(__name__)

app.secret_key = 'your_secret_key_here'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_here'
jwt = JWTManager(app)

try:
    connection = psycopg2.connect(os.environ["DATABASE_URL"])
except psycopg2.OperationalError as e:
    print(f"Error connecting to the database: {e}")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)

@app.route('/admin',methods=['GET'])
def admin(): 
    username = session.get('username')
    if not username : 
        return redirect(url_for('login'))
    if username != 'admin' : 
        return render_template('function.html',userName=username)
    if username == 'admin' :
        try:
            with connection.cursor() as cursor:
                cursor.execute('use project_database')
                query = '''SELECT * FROM users'''
                cursor.execute(query)
                userData = cursor.fetchall()
                print(userData)
                userdata = []
                for user in userData:
                    User = {
                        'Username':user[0],
                        'Email':user[1],
                        'Name':user[2]
                    }
                    userdata.append(User)
                print(userdata)
            
            return render_template('admin.html', username='admin', userData=userdata)
        except Exception as e:
            # If an error occurs, return an error message or log it
            return jsonify({'error': str(e)})

@app.route('/')
def welcome():
    username = session.get('username')
    if username: 
        return render_template('function.html',userName=username)
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
        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin'))
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Users WHERE Username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            if user is not None:
                retrieve_password = user[3]
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
            Image_Id SERIAL PRIMARY KEY,
            Username VARCHAR(255) NOT NULL,
            Image_name VARCHAR(255) NOT NULL,
            Filetype VARCHAR(100) NOT NULL,
            Img BYTEA NOT NULL
            );'''

            cursor.execute(create_image_table)
            
        
            for image in images:

                if image.filename and allowed_file(image.filename):
                    cursor.execute("SELECT * FROM Images WHERE Username = %s and Image_name = %s",(username,image.filename))
                    existing_image = cursor.fetchall()
                    if existing_image:
                        # exist_img = {
                        #     'Image_Id': existing_image[0],
                        #     'Username': existing_image[1],
                        #     'Image_name': existing_image[2],
                        #     'Filetype': existing_image[3],
                        #     'Img': existing_image[4]
                        # }
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
        create_image_table = '''CREATE TABLE IF NOT EXISTS Images (
            Image_Id SERIAL PRIMARY KEY,
            Username VARCHAR(255) NOT NULL,
            Image_name VARCHAR(255) NOT NULL,
            Filetype VARCHAR(100) NOT NULL,
            Img BYTEA NOT NULL
            );'''

        cursor.execute(create_image_table)
    
        sql = "SELECT Image_name, Img, Filetype FROM Images WHERE username = %s"
        cursor.execute(sql, (username,))
        results = cursor.fetchall()

        if not results:
            return jsonify({'error': 'User not found in the database.'}), 404

        # images_data = [{'filename': result['Image_name'], 'format': result['Filetype'].split('/')[1].lower(), 'data': base64.b64encode(result.get('Img')).decode('utf-8')} for result in results]
        images_data = [
            {
                'filename': result[0],  # Assuming Image_name is the first element of the tuple
                'format': result[2].split('/')[1].lower(),  # Assuming Filetype is the second element of the tuple
                'data': base64.b64encode(result[1]).decode('utf-8') if result[1] is not None else None  # Assuming Img is the third element of the tuple
            }
            for result in results
        ]

        if not images_data:
            return jsonify({'error': 'Image data not found in the database.'}), 404

        return jsonify({'images': images_data})


@app.route('/function/<userName>', methods=['GET', 'POST'])
def function(userName):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
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
        username = session.get('username')
        if not username:
            # return jsonify({'error': 'User not logged in'}), 401
            return redirect(url_for('login'))
        return render_template('video.html',userName = username)

@app.route('/get_audio_from_database')
def get_all_audio():
    try:
        # Connect to the database
        # connection = pymysql.connect(host=mysql_host,user=mysql_user,password = mysql_password,db=mysql_db,cursorclass=pymysql.cursors.DictCursor)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT Audio_id FROM Audio")
            id = [f[0] for f in cursor.fetchall()]

            return jsonify({'id':id})
    except Exception as ex: 
        return jsonify({"Error": f'{ex} has occured.'})





@app.route('/audio/<id>')
def serve_audio(id):

    # connection = pymysql.connect(host=mysql_host,user=mysql_user,password = mysql_password,db=mysql_db,cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        try:
            query = "SELECT AudioData FROM Audio WHERE Audio_id = %s"
            cursor.execute(query, (id))
            audio_data = cursor.fetchone()[0]
            print(1213)
            if audio_data:
                print('audio_data')
                return send_file(BytesIO(audio_data), mimetype='audio/mp3')
            else: 
                return jsonify({'Error': 'Audio file was not found.'}), 404
        except Exception as e:
            return jsonify({'Error':f'{e} as occured.'}), 404
        


@app.route('/create_video', methods=['GET' , 'POST'])
def create_video():
    selected_images_blobs = request.form.getlist('selectedImagesBlobs[]')
    selected_audio_ids = request.form.getlist('selectedAudioFilesIds[]')
    selected_resolution = request.form.get('resolution')
    print(selected_resolution)
    selected_transition = request.form.get('transition')
    print(selected_audio_ids)
    print(selected_transition)

    audio_clips= []
    with connection.cursor() as cursor:
        audio_blobs = []
        for id in selected_audio_ids:
            sql = '''SELECT AudioData FROM Audio WHERE Audio_id = %s '''
            cursor.execute(sql,(id))
            audio_data = cursor.fetchone()[0]
            audio_blobs.append(BytesIO(audio_data))
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
    
    image_arrays_resized = []
    for img in image_files:
        if selected_resolution == '144p':
            resized_img = img.resize((256, 144))
        elif selected_resolution == '360p':
            resized_img = img.resize((480,360))
        elif selected_resolution == '720p':
            resized_img = img.resize((1280, 720))
        elif selected_resolution == '1080p':
            resized_img = img.resize((1920, 1080))

        if resized_img.mode == 'RGBA':
            resized_img = resized_img.convert('RGB')
        image_arrays_resized.append(np.array(resized_img))

    num_frames = len(image_arrays_resized)
    fps = 30
    duration_per_frame = 2.5
    durations = [duration_per_frame] * num_frames    
    video_clip=apply_transitions(image_arrays_resized,durations,selected_transition)
    
    if len(audio_clips) > 1:
        audio_clip = concatenate_audioclips(audio_clips)
    elif len(audio_clips) == 1:
        audio_clip = audio_clips[0]
    else:
        audio_clip = None

    if audio_clip:
        audio_duration = audio_clip.duration
        video_duration = video_clip.duration
        if audio_duration < video_duration:
            # Calculate how many times to repeat the audio clip
            num_repeats = int(np.ceil(video_duration / audio_duration))
            # Concatenate the audio clip with itself multiple times
            audio_cliping = [audio_clip for i in range(num_repeats)]
            repeated_audio_clip = concatenate_audioclips(audio_cliping)
            # Set the duration of the concatenated audio clip to match the video duration
            repeated_audio_clip = repeated_audio_clip.set_duration(video_duration)
            # Set the audio of the video clip
            video_clip = video_clip.set_audio(repeated_audio_clip)

            # Set the audio of the video clip
            # video_clip = video_clip.set_audio(audio_clip)
        else: 
            audio_clip = audio_clip.set_duration(audio_duration)
            video_clip = video_clip.set_audio(audio_clip)
        print('video_clip')

    output_video_filename = 'output_video.mp4'
    video_clip.write_videofile(output_video_filename, codec='libx264', fps=fps)

    # Read the video file and extract blob
    with open(output_video_filename, 'rb') as file:
        video_blob = file.read()

    # Delete the video file
    os.remove(output_video_filename)

    video_base64 = base64.b64encode(video_blob).decode('utf-8')
    response_data = {
        'video_base64': video_base64,
        'mime_type': 'video/mp4'  
    }
    return jsonify(response_data)

def apply_transitions (images,durations,transition_name):
    clips_with_transitions = []
    num_frames = len(images)

    if transition_name == "fade":
        for i in range(num_frames):
            clip = ImageClip(images[i], duration=durations[i])
            if i > 0:
                clip = clip.fadein(0.75)
                clips_with_transitions[-1] = clips_with_transitions[-1].fadeout(0.75)
                
            clips_with_transitions.append(clip) 
        video_clip = concatenate_videoclips(clips_with_transitions)
        print("hello")
        return video_clip
    elif transition_name == "none":
        video_clip = ImageSequenceClip(images,durations=durations)
        return video_clip
    
    
    # Delete the temporary file
    
    
    # return send_file(BytesIO(video_blob), mimetype='video/mp4', as_attachment=True,download_name='output_video.mp4')



@app.route('/logout')
def logout():
     session.pop('token', None)
     session.pop('username',None)
     return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True, port=5010)
