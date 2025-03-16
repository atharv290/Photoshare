from flask import Flask, render_template, request, redirect, url_for,jsonify,session
from flask_mysqldb import MySQL
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import random
import datetime
import string
def generate_random_code(length=8):
    characters = string.ascii_letters + string.digits  # Combine letters and digits
    return ''.join(random.choices(characters, k=length))

# Example usag
app = Flask(__name__)
# Set the directory for image uploads
app.config['UPLOAD_FOLDER'] = 'public_html/static/uploads'
# Set allowed file extensions for security
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
# Check if the file is an allowed image format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#import mysql.connector
app.secret_key = '1234'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sen_project'
Mysql = MySQL(app)
# Home Page
@app.route('/')
def home():
    if 'email' in session:
        return render_template('HomePage.html')
    return render_template('index.html')  # Main home page
#handle Signup Logic
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        # Hash the password
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        cur = Mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO user_logins (Full_Name, Email, Password) VALUES (%s, %s, %s)",
                (name, email, password_hash)
            )
            Mysql.connection.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return f"Error: {e}", 500
        finally:
            cur.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Hash the entered password for comparison
        hash_p = hashlib.sha256(password.encode("utf-8")).hexdigest()
        cur = Mysql.connection.cursor()
        try:
            cur.execute("SELECT Email, Password FROM user_logins WHERE Email = %s", (email,))
            user = cur.fetchone()
            if user and hash_p == user[1]:  # Compare hashed passwords
                session['email'] = user[0]  # Store email in session
                return redirect(url_for('home'))
            else:
                return render_template('index.html', error="Invalid email or password")
        except Exception as e:
            return f"Error: {e}", 500
        finally:
            cur.close()
    return render_template('index.html')
#handle logout Logic
@app.route('/logout')
def logout():
    session.pop('admin_email',None)
    session.pop('email',None)
    return redirect(url_for('home'))

#handle Admin Signup Logic
@app.route('/admin_s',methods= ['GET','POST'])
def admin_s():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cur = Mysql.connection.cursor()
        cur.execute(
    "INSERT INTO admin_logins (Full_Name, Email, Password) VALUES (%s, %s, %s)",
    (name, email, password))
        Mysql.connection.commit()
        cur.close()
        return render_template('admin.html')
    return render_template('admin.html')

#handle Admin login Logic
@app.route('/admin_l', methods=['GET', 'POST'])
def admin_l():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = Mysql.connection.cursor()
        cur.execute("SELECT Email, Password FROM admin_logins WHERE Email = %s", (email,))
        user = cur.fetchone()
        cur.execute("SELECT Full_Name, bio, profile_img FROM admin_logins WHERE Email = %s", (email,))
        user1 = cur.fetchone()
        cur.close()
        if user1:
            profile_data = {
                'name': user1[0], 
                'bio': user1[1],   
                'profile_img': user1[2] if user1[2] else "static/uploads/default-profile.jpg"
            }
        else:
            profile_data = None  
        if user and password == user[1]:  
            session['admin_email'] = user[0]
            return render_template('adminHome.html', profile=profile_data)
        else:
            return render_template('admin.html')
    return render_template('admin.html')

#loads Admin Signup and login page 
@app.route('/admin')
def admin_loging():
    return render_template('admin.html')
#handle Admin Signup Logic
@app.route('/upload_photos', methods=['POST'])
def upload_files():
    files = request.files.getlist('photos')
    cost = request.form['cost']
    if not files:
        return "No files uploaded!", 400
    # Create the 'uploads' directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    random_code = generate_random_code()
    status = request.form['status']
    print(status)
    try:
        cur = Mysql.connection.cursor()
        if(status=='private'):
            email =request.form['clientEmail']
            name = request.form['clientName']
            mobile =request.form['clientMobile']
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)  # Save the file to the server's folder
                    date = datetime.datetime.now()  # Current datetime
                    # Insert the file path into the database
                    query = "INSERT INTO uploads_details (client_name, client_email,client_no,date) VALUES (%s, %s,%s, %s,%s)"
                    cur.execute(query, (name, email,mobile,date))
                    query = "INSERT INTO images2 (image_path, filename,Status,code,client_email,Date,client_name,client_no,price) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s)"
                    cur.execute(query, (file_path, filename,status,random_code,email,date,name,mobile,cost))
            Mysql.connection.commit()
            return "Files uploaded and paths stored in the database successfully!", 200
        else:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)  # Save the file to the server's folder
                    date = datetime.datetime.now()  # Current datetime
                    # Insert the file path into the database
                    query = "INSERT INTO images2 (image_path, filename,Status,Date,price) VALUES (%s, %s,%s, %s, %s)"
                    cur.execute(query, (file_path, filename,status,date,cost))
            Mysql.connection.commit()
            return "Files uploaded and paths stored in the database successfully!", 200
    except Exception as err:
        return f"Error: {err}", 500
    finally:
        cur.close()

@app.route('/marketplace', methods=['POST'])
def loadpage():
    access_code = request.form['secretCode']
    access_type = request.form['accessType']
    session['secretCode'] = access_code
    session['accessType'] = access_type
    return render_template('marketplace.html')
# Image Serving Route
@app.route('/get-images', methods=['GET'])
def get_images():
    try:
        cur = Mysql.connection.cursor()
        
        if session.get('accessType') == 'private':
            query = "SELECT filename, image_path, price FROM images2 WHERE code = %s"
            cur.execute(query, (session['secretCode'],))
        else:
            query = "SELECT filename, image_path, price FROM images2 WHERE Status = %s"
            cur.execute(query, ('public',))  # Assuming 'public' status for non-private images

        rows = cur.fetchall()
        
        if not rows:
            return jsonify({'message': 'No images found'}), 404
        
        images = []
        for row in rows:
            filename, image_path, price = row  # Ensure correct unpacking
            image_url = f"static/uploads/{filename}"  # Construct the URL for accessing the image
            
            images.append({
                'url': image_url,
                'filename': filename,
                'price': price  # Include price in the response
            })

        return jsonify({'images': images}), 200
    
    except Exception as err:
        print(f"Error occurred in get_images: {err}")  # Log the error
        return jsonify({'error': str(err)}), 500
    
    finally:
        if 'cur' in locals() and cur:
            cur.close()


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'admin_email' not in session:
        return "Unauthorized", 403  
    new_name = request.form.get('name')
    new_bio = request.form.get('bio')
    file = request.files.get('profile_pic')
    if file and file.filename != '' and allowed_file(file.filename):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Normalize path for cross-platform support (always use forward slashes `/`)
        file_path = file_path.replace("\\", "/") 
        file.save(file_path)  # Save the file
        relative_path = f"static/uploads/{filename}" #Ensure it's relative
        try:
            cur = Mysql.connection.cursor()
            query = "UPDATE admin_logins SET Full_Name = %s, profile_img = %s, bio = %s WHERE Email = %s"
            cur.execute(query, (new_name, relative_path, new_bio, session['admin_email']))
            Mysql.connection.commit()
            return jsonify({"message": "Profile updated successfully"}), 200
        except Exception as err:
            return f"Error: {err}", 500
        finally:
            cur.close()
    return "Invalid file or no file uploaded!", 400
@app.route('/get-images-photographer', methods=['GET'])
def get_images_photographer():
    try:
        cur = Mysql.connection.cursor()
        #caption	Email	Likes	post
        query = "SELECT caption,post,Likes,filename FROM photographer_posts WHERE Email = %s"
        cur.execute(query, (session['admin_email'],))  # Assuming 'public' status for non-private images
        rows = cur.fetchall()
        if not rows:
            return jsonify({'message': 'No images found'}), 404
        
        images = []
        for row in rows:
            caption, post, likes,filename = row  # Ensure correct unpacking
            image_url = f"static/uploads/{filename}" # Construct the URL for accessing the image
            images.append({
                'url': image_url,
                'caption':caption,
                'likes': likes  # Include price in the response
            })

        return jsonify({'images': images}), 200
    
    except Exception as err:
        print(f"Error occurred in get_images: {err}")  # Log the error
        return jsonify({'error': str(err)}), 500
    
    finally:
        if 'cur' in locals() and cur:
            cur.close()
@app.route('/post_img', methods=['POST'])
def post_images():
    files = request.files.getlist('Post_imgs')
    Caption = request.form['caption']
    email = session['admin_email']
    if not files:
        return "No files uploaded!", 400
    # Create the 'uploads' directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    print(Caption)
    try:
        cur = Mysql.connection.cursor()
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)  # Save the file to the server's folder
                date = datetime.datetime.now()  # Current datetime
                # Insert the file path into the database
                #	caption	Email	Likes	post
                query = "INSERT INTO photographer_posts (caption, post, Email, filename) VALUES (%s, %s, %s,%s)"
                cur.execute(query, (Caption, file_path, email,filename))
            Mysql.connection.commit()
            return "Files uploaded and paths stored in the database successfully!", 200
    except Exception as err:
        return f"Error: {err}", 500
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)
