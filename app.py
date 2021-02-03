from flask import Flask, render_template, json, request, flash, send_from_directory #general imports
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES #imports for uploading images
from werkzeug import generate_password_hash, check_password_hash #imports for encrypting passwords
import sqlite3 #import sqlite
import datetime #import datetime for image upload timestamp
import os #import for operating system functionality

#create application
app = Flask(__name__)

#connect to database
conn = sqlite3.connect('PhotoGarage.db')
print "Opened database successfully"

#return homepage
@app.route("/")
def main():
    return render_template('index.html')

#return sign up page
@app.route('/signup')
def signup():
    return render_template('signup.html')

#open specific page of photo gallery
@app.route('/viewer/<int:page_num>')
def viewer(page_num):
    conn = sqlite3.connect('PhotoGarage.db')
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute("SELECT PHOTOPATH FROM tblPhotos ORDER BY UPLOADDATE desc")
    image_names = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT CAPTION FROM tblPhotos ORDER BY UPLOADDATE desc")
    image_captions = [r[0] for r in cursor.fetchall()]
    return render_template('viewer.html', image_names=image_names, image_captions=image_captions, page_num=page_num)

#add new user to the users table in the database
@app.route('/newUser',methods=['POST'])
def newUser():
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    if _name and _email and _password:
        conn = sqlite3.connect('PhotoGarage.db')
        c = conn.cursor()
        userInfo = [(_name, _email, generate_password_hash(_password))]
        c.executemany("INSERT INTO tblUsers (NAME, EMAIL, PASSWORD) VALUES (?,?,?)", userInfo)
    	data = c.fetchall()
    	if len(data) is 0:
    		conn.commit()
    		return render_template('userAdded.html')
    	else:
    		return render_template('error.html')
    else:
        return render_template('error.html')

#configure uploaded photo destination
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

#upload photo and optional caption 
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        caption = request.form['caption']
        user = "visitor"
        currentTime = datetime.datetime.now()
        if filename:
            conn = sqlite3.connect('PhotoGarage.db')
            c = conn.cursor()
            photoInfo = [(filename, caption, user, currentTime.isoformat())]
            c.executemany("INSERT INTO tblPhotos (PHOTOPATH, CAPTION, USER, UPLOADDATE) VALUES (?,?,?,?)", photoInfo)
            data=c.fetchall()
            if len(data) is 0:
            	conn.commit()
            	return render_template('complete.html', image_name=filename)
            else:
            	return render_template('error.html')
        else:
            return render_template('error.html')
    return render_template('upload.html')

#send uploaded photo from directory that was configured
@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("static/img", filename)

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

if __name__ == "__main__":
    app.run(debug=True)

conn.close()