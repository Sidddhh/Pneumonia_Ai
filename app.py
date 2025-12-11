from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import requests  # For reCAPTCHA
import uuid
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Load .env FIRST
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load Model
#model_path = "model/best_vgg_model.keras"
#model = load_model(model_path)
#print("✅ Model loaded successfully!")
# lazy-load model (do NOT load at import time)
model = None

def get_model():
    """Load the model on first use and cache it."""
    global model
    if model is None:
        print("📌 Loading model into memory...")
        model = load_model(model_path)
        print("✅ Model loaded (lazy).")
    return model

# lightweight health endpoint for smoke tests
@app.route('/health')
def health():
    return 'OK', 200


# DB Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authority_id = db.Column(db.String(36), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    hospital_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_pic = db.Column(db.String(200), default='default-avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(36), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    xray_date = db.Column(db.String(20), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Env vars
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')
GMAIL_USER = os.getenv('GMAIL_USER', 'your-gmail@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'your-app-password')

os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/uploads/avatars', exist_ok=True)

def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def send_email(to_email, authority_id, password, authority_name):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = 'Pneumonia AI - Your Authority Portal Credentials'

    body = f"""
    Dear {authority_name},

    Thank you for registering as an authority with Pneumonia AI.

    Your Authority ID: {authority_id}
    Temporary Password: {password}

    Please login to our portal using these credentials and change your password immediately.
    Login URL: http://127.0.0.1:5000/login

    Best regards,
    Pneumonia AI Team
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@app.route('/')
def home():
    if 'authority_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

    if request.method == 'POST':
        if 'consent' not in request.form:
            flash('You must agree to the terms and conditions.', 'error')
            return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA.', 'error')
            return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        if RECAPTCHA_SECRET_KEY:
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            verify_data = {
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response,
                'remoteip': request.remote_addr
            }
            response = requests.post(verify_url, data=verify_data)
            result_json = response.json()
            if not result_json.get('success'):
                flash('reCAPTCHA verification failed. Please try again.', 'error')
                return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        full_name = request.form.get('full_name', '').strip()
        hospital_name = request.form.get('hospital_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', '')

        if not all([full_name, hospital_name, email, role]):
            flash('Please fill all required fields.', 'error')
            return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        authority_id = str(uuid.uuid4()).replace('-', '').upper()[:8]
        password = generate_password()

        try:
            password_hash = generate_password_hash(password)
            new_user = User(
                authority_id=authority_id,
                full_name=full_name,
                hospital_name=hospital_name,
                email=email,
                role=role,
                password_hash=password_hash
            )
            db.session.add(new_user)
            db.session.commit()
            email_sent = send_email(email, authority_id, password, full_name)
            result_msg = f"Authority registered successfully! Role: {role} at {hospital_name}."
            if email_sent:
                flash(f'{result_msg} Credentials emailed to {email}.', 'success')
            else:
                flash(f'{result_msg} but email failed. ID: {authority_id}, Temp Password: {password}', 'warning')
            return render_template('register.html', result=result_msg, authority_id=authority_id, recaptcha_site_key=RECAPTCHA_SITE_KEY)
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

    return render_template('register.html', result=None, recaptcha_site_key=RECAPTCHA_SITE_KEY)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['authority_id'] = user.authority_id
            session['full_name'] = user.full_name
            session['role'] = user.role
            session['hospital_name'] = user.hospital_name
            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'authority_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(authority_id=session['authority_id']).first()
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('dashboard.html', user=user, patients=patients)



# ===========================
# ✅ Patient Management Routes
# ===========================
@app.route('/upload_patient', methods=['POST'])
def upload_patient():
    if 'authority_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        name = request.form.get('name')
        age = request.form.get('age')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        xray_date = request.form.get('xray_date')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        file = request.files.get('image')

        print("📥 Received form data:", name, age, city, state, pincode, xray_date, mobile, email)

        if not all([name, age, city, state, pincode, xray_date, mobile, email]) or not file:
            print("❌ Missing fields or image")
            return jsonify({'success': False, 'error': 'Missing required fields or image'})

        # Save image securely
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        img_path = os.path.join('static/uploads', unique_filename)
        file.save(img_path)
        print("✅ Image saved:", img_path)

        # Preprocess for model prediction
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = get_model().predict(img_array, verbose=0)[0][0]
        result = "Pneumonia" if prediction > 0.5 else "Normal"
        confidence = (prediction if result == "Pneumonia" else 1 - prediction) * 100
        confidence = round(float(confidence), 2)
        print(f"🧠 Model Prediction: {result} ({confidence}%)")

        patient_id = str(uuid.uuid4()).replace('-', '').upper()[:8]

        new_patient = Patient(
            patient_id=patient_id,
            name=name,
            age=int(age),
            city=city,
            state=state,
            pincode=pincode,
            xray_date=xray_date,
            mobile=mobile,
            email=email,
            image_path=unique_filename,
            result=result,
            confidence=confidence
        )

        db.session.add(new_patient)
        db.session.commit()
        print(f"✅ Added to DB: {name} ({patient_id})")

        return jsonify({
            'success': True,
            'result': str(result),
            'confidence': float(confidence),
            'patient_id': patient_id
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ Upload error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/get_patient/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Fetch a single patient record by ID"""
    if 'authority_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404

    return jsonify({
        'success': True,
        'patient': {
            'id': patient.id,
            'patient_id': patient.patient_id,
            'name': patient.name,
            'age': patient.age,
            'city': patient.city,
            'state': patient.state,
            'pincode': patient.pincode,
            'xray_date': patient.xray_date,
            'mobile': patient.mobile,
            'email': patient.email,
            'image_path': patient.image_path,
            'result': patient.result,
            'confidence': patient.confidence
        }
    })

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """Edit patient record"""
    if 'authority_id' not in session:
        return redirect(url_for('login'))

    # ✅ Get the currently logged-in user (from the User model, not Authority)
    user = User.query.filter_by(authority_id=session['authority_id']).first()

    # ✅ Fetch the patient by ID
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        try:
            patient.name = request.form['name']
            patient.age = int(request.form['age'])
            patient.city = request.form['city']
            patient.state = request.form['state']
            patient.pincode = request.form['pincode']
            patient.xray_date = request.form['xray_date']
            patient.mobile = request.form['mobile']
            patient.email = request.form['email']

            db.session.commit()
            flash('✅ Patient record updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error updating record: {e}', 'danger')

    return render_template('edit_patient.html', patient=patient, user=user)


@app.route('/update_patient', methods=['POST'])
def update_patient():
    if 'authority_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    patient_id = request.form.get('patientId')
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404

    try:
        patient.name = request.form.get('name', patient.name)
        patient.age = int(request.form.get('age', patient.age))
        patient.city = request.form.get('city', patient.city)
        patient.state = request.form.get('state', patient.state)
        patient.pincode = request.form.get('pincode', patient.pincode)
        patient.xray_date = request.form.get('xray_date', patient.xray_date)
        patient.mobile = request.form.get('mobile', patient.mobile)
        patient.email = request.form.get('email', patient.email)

        # Optional: Update image if provided
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            img_path = os.path.join('static/uploads', unique_filename)
            file.save(img_path)
            patient.image_path = unique_filename

        db.session.commit()
        print(f"✅ Patient {patient.patient_id} updated successfully!")
        return jsonify({'success': True, 'message': 'Patient updated successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"❌ Update error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/delete_patient/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete patient record"""
    if 'authority_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404

    try:
        # Remove stored image file
        img_path = os.path.join('static/uploads', patient.image_path)
        if os.path.exists(img_path):
            os.remove(img_path)

        db.session.delete(patient)
        db.session.commit()
        print(f"🗑️ Deleted patient record: {patient.patient_id}")
        return jsonify({'success': True, 'message': 'Patient deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"❌ Delete error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    



# Settings Routes
@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    if 'authority_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    user = User.query.filter_by(authority_id=session['authority_id']).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    file = request.files.get('profile_pic')
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No file uploaded'})

    filename = secure_filename(file.filename)
    if filename != '':
        unique_filename = f"{user.authority_id}_{filename}"
        file_path = os.path.join('static/uploads/avatars', unique_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        user.profile_pic = f"uploads/avatars/{unique_filename}"
        db.session.commit()
        return jsonify({'success': True, 'profile_pic': user.profile_pic})
    return jsonify({'success': True, 'filename': new_filename})


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'authority_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    user = User.query.filter_by(authority_id=session['authority_id']).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not old_password or not new_password or not confirm_password:
        return jsonify({'success': False, 'error': 'All fields required'})

    if new_password != confirm_password:
        return jsonify({'success': False, 'error': 'New passwords do not match'})

    if len(new_password) < 8:
        return jsonify({'success': False, 'error': 'New password must be at least 8 characters'})

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'success': False, 'error': 'Old password incorrect'})

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    if 'authority_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    user = User.query.filter_by(authority_id=session['authority_id']).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    # Delete user
    db.session.delete(user)
    db.session.commit()

    session.clear()
    return jsonify({'success': True, 'message': 'Account deleted successfully'})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/analytics')
def analytics():
    if 'authority_id' not in session:
        return redirect(url_for('login'))

    # Get user info
    user = User.query.filter_by(authority_id=session['authority_id']).first()

    # Total patients
    total_patients = Patient.query.count()

    # Pneumonia vs Normal
    pneumonia_cases = Patient.query.filter_by(result='Pneumonia').count()
    normal_cases = Patient.query.filter_by(result='Normal').count()

    # Average confidence
    avg_confidence = round(db.session.query(db.func.avg(Patient.confidence)).scalar() or 0, 2)

    # Distribution by state
    state_distribution = (
        db.session.query(Patient.state, db.func.count(Patient.id))
        .group_by(Patient.state)
        .all()
    )
    states = [s[0] for s in state_distribution]
    counts = [s[1] for s in state_distribution]

    # Patient records for the table
    patients = Patient.query.all()

    return render_template(
        'analytics.html',
        user=user,
        patients=patients,
        total_patients=total_patients,
        pneumonia_cases=pneumonia_cases,
        normal_cases=normal_cases,
        avg_confidence=avg_confidence,
        states=states,
        counts=counts
    )



if __name__ == '__main__':
    app.run(debug=True)