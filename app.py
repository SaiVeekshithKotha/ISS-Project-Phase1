from flask import Flask, render_template, redirect, url_for, request, abort, session, make_response,jsonify,send_file
import requests
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from io import BytesIO
from PIL import Image
import base64
import os
import numpy as np
from moviepy.editor import CompositeVideoClip,ImageClip,ImageSequenceClip,concatenate_videoclips, concatenate_audioclips, AudioFileClip,ColorClip
from moviepy.video.fx.resize import resize

# from moviepy.video.compositing.transitions import crossfade
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
            audio_data = cursor.fetchone()['AudioData']
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
    duration_per_frame = 5
    durations = [duration_per_frame] * num_frames    
    video_clip=apply_transitions(image_arrays_resized,durations,selected_transition)
    
    if len(audio_clips) > 1:
        audio_clip = concatenate_audioclips(audio_clips)
    elif len(audio_clips) == 1:
        audio_clip = audio_clips[0]
    else:
        audio_clip = None

    if audio_clip:
        audio_duration = video_clip.duration
        audio_clip = audio_clip.set_duration(audio_duration)

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
                clip = clip.fadein(2)
                clips_with_transitions[-1] = clips_with_transitions[-1].fadeout(2)
                
            clips_with_transitions.append(clip) 
        video_clip = concatenate_videoclips(clips_with_transitions)
        print("hello")
        return video_clip
    elif transition_name == "none":
        video_clip = ImageSequenceClip(images,durations=durations)
        return video_clip
    
    
    # elif transition_name=="zoom_in_out":
    #     clips_with_transitions.append(ImageClip(images[0]).set_duration(durations[0]))
    #     for i in range(num_frames-1):
    #         clip = zoom_in_out_transition(ImageClip(images[i]), ImageClip(images[i+1]), durations[i])
    #         clips_with_transitions.append(clip)
    #     clips_with_transitions.append(ImageClip(images[i+1]).set_duration(durations[i+1]))
    #     return concatenate_videoclips(clips_with_transitions)
        
    #     for i in range(num_frames):
    #         clip = ImageClip(image_arrays_resized[i], duration=durations[i])
    #         clips_with_transitions.append(clip)

    #     # Apply transitions between clips
    #     for i in range(1, num_frames):
    #         transition_duration = 2  # Adjust as needed
    #         zoom_in_clip = clips_with_transitions[i].resize(lambda t: 1.1 + 0.1 * t / transition_duration)
    #         zoom_out_clip = clips_with_transitions[i - 1].resize(lambda t: 1.1 + 0.1 * (transition_duration - t) / transition_duration)
    #         transition_clip = concatenate_videoclips([zoom_out_clip.set_duration(transition_duration / 2),zoom_in_clip.set_duration(transition_duration / 2)])
    #         clips_with_transitions[i - 1] = clips_with_transitions[i - 1].set_end(durations[i - 1] - transition_duration)
    #         clips_with_transitions[i] = clips_with_transitions[i].set_start(durations[i - 1])
    #         clips_with_transitions[i] = concatenate_videoclips([transition_clip, clips_with_transitions[i]])
        
    # # Concatenate the clips with transitions
    #     video_clip = concatenate_videoclips(clips_with_transitions)
    #     return video_clip
    
    # elif transition_name=="slide":
    #     for i in range(num_frames):
    #         clip = ImageClip(images[i], duration=durations[i])
    #         clips_with_transitions.append(clip)
        

    #     # Apply slide effect between clips
    #     slide_duration = 2.5  # Adjust as needed
    #     for i in range(1, num_frames):
    #         slide_in_clip = clips_with_transitions[i - 1].fx(resize, width=lambda t: int(clip.w * (1 - t / slide_duration)), height=clip.h)
    #         slide_out_clip = clips_with_transitions[i].fx(resize, width=lambda t: int(clip.w * (t / slide_duration)), height=clip.h)
    #         transition_clip = concatenate_videoclips([slide_out_clip.set_start(0), slide_in_clip.set_start(slide_duration)])
    #         clips_with_transitions[i - 1] = transition_clip.set_end(durations[i - 1] - slide_duration)
    #         clips_with_transitions[i] = clips_with_transitions[i].set_start(durations[i - 1])

    #     # Concatenate the clips with transitions

    #     video_clip = concatenate_videoclips(clips_with_transitions)
    #     return video_clip

# def zoom_in_out_transition(image1, image2, duration):
#     zoom_in = (image2.resize((image1.size[0], image1.size[1])).set_position(('center', 'center')).set_duration(duration / 2))
#     zoom_out = (image2.set_position(('center', 'center')).resize((image1.size[0], image1.size[1])).set_duration(duration / 2))
#     return concatenate_videoclips([zoom_in, zoom_out])


        
@app.route('/logout')
def logout():
     session.pop('token', None)
     session.pop('username',None)
     return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

