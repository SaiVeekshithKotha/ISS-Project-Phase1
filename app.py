from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/registration.html',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        return "Hello"


@app.route('/login.html', methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/function.html', methods=['GET', 'POST'])
def function():
    return render_template('function.html')

@app.route('/video.html', methods=['GET', 'POST'])
def video():
    return render_template('video.html')


if __name__ == '__main__':
    app.run(debug=True)