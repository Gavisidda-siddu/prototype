from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import re
import os
import pandas as pd
import joblib
import numpy as np
import os.path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {
    'diabetes': 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/data/users.db')
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'pdf'}
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    contact_messages = db.relationship('ContactMessage', backref='user', lazy=True)
    prescriptions = db.relationship('Prescription', backref='user', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    doctor = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prescriptions = db.relationship('Prescription', backref='appointment', lazy=True)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DiabetesUser(db.Model):
    __bind_key__ = 'diabetes'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    glucose = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.String(50), nullable=False)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)
    patient_name = db.Column(db.String(100), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# Load diabetes model and scaler
model = joblib.load('static/model/diabetes_model.pkl')
scaler = joblib.load('static/model/scaler.pkl')

# Load diet and exercise recommendation datasets
diet_df = pd.read_csv('static/data/diabetes_diet_dataset_indian_modified.csv')
exercise_df = pd.read_csv('static/data/exercise_recommendations.csv')

# Custom Jinja2 filters
@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)

@app.template_filter('splitext')
def splitext_filter(path):
    return os.path.splitext(path)[1][1:]  # Get extension without dot

# Helper functions
def get_diet_recommendation(glucose):
    if glucose < 100:
        category = 'Normal'
    elif 100 <= glucose < 126:
        category = 'Prediabetic'
    else:
        category = 'Diabetic'
    matching_diets = diet_df[diet_df['sugar_category'] == category]
    if not matching_diets.empty:
        diet_row = matching_diets.sample(n=1).iloc[0]
        return {
            'diet': diet_row['recommended_diet'],
            'foods': diet_row['example_foods_indian'].split(', '),
            'category': category
        }
    return {
        'diet': 'Consult a doctor',
        'foods': ['Consult a doctor'],
        'category': category
    }

def get_exercise_recommendation(age, weight, glucose, bmi):
    if glucose < 100:
        sugar_category = 'Normal'
    elif 100 <= glucose < 126:
        sugar_category = 'Prediabetic'
    else:
        sugar_category = 'Diabetic'
    if bmi >= 30 or sugar_category == 'Diabetic':
        exercise_category = 'Light'
    elif bmi >= 25 or sugar_category == 'Prediabetic':
        exercise_category = 'Moderate'
    else:
        exercise_category = 'Intense' if age < 30 else 'Moderate'
    matching_exercises = exercise_df[exercise_df['category'] == exercise_category]
    if matching_exercises.empty:
        return ['No matching exercise plan found. Consult a doctor.']
    matching_exercises['age_diff'] = np.abs(matching_exercises['age'] - age)
    matching_exercises['weight_diff'] = np.abs(matching_exercises['weight'] - weight)
    matching_exercises['total_diff'] = matching_exercises['age_diff'] + matching_exercises['weight_diff']
    best_match = matching_exercises.sort_values('total_diff').iloc[0]
    return best_match['exercise_plan'].split(', ')

def validate_inputs(age, glucose, weight, height):
    errors = []
    if not (1 <= age <= 120):
        errors.append('Age must be between 1 and 120.')
    if not (0 <= glucose <= 500):
        errors.append('Glucose must be between 0 and 500 mg/dL.')
    if not (20 <= weight <= 300):
        errors.append('Weight must be between 20 and 300 kg.')
    if not (0.5 <= height <= 3.0):
        errors.append('Height must be between 0.5 and 3.0 meters.')
    return errors

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('Please log in or register to access the home page.', 'info')
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

@app.route('/services')
def services():
    if 'user_id' not in session:
        flash('Please log in or register to access this page.', 'info')
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    return render_template('services.html', user=user)

@app.route('/doctors')
def doctors():
    if 'user_id' not in session:
        flash('Please log in or register to access this page.', 'info')
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    return render_template('doctor.html', user=user)

@app.route('/faqs')
def faqs():
    if 'user_id' not in session:
        flash('Please log in or register to access this page.', 'info')
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    return render_template('faqs.html', user=user)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'user_id' not in session:
        flash('Please log in or register to access this page.', 'info')
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        errors = {}
        if not name:
            errors['name'] = 'Please enter your name'
        if not email or not re.match(r'^\S+@\S+\.\S+$', email):
            errors['email'] = 'Please enter a valid email address'
        if not message:
            errors['message'] = 'Please enter your message'
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        contact_message = ContactMessage(
            user_id=user.id,
            name=name,
            email=email,
            message=message
        )
        db.session.add(contact_message)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message sent successfully!'})
    return render_template('contact.html', user=user)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'user_id' not in session:
        flash('Please log in or register to access this page.', 'info')
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        data = request.get_json()
        fullname = data.get('fullname')
        email = data.get('email')
        phone = data.get('phone')
        doctor = data.get('doctor')
        date = data.get('date')
        time = data.get('time')
        reason = data.get('reason')
        errors = {}
        if not fullname:
            errors['fullname'] = 'Please enter your full name'
        if not email or not re.match(r'^\S+@\S+\.\S+$', email):
            errors['email'] = 'Please enter a valid email address'
        if not phone or not re.match(r'^\d{10,15}$', phone.replace('-', '')):
            errors['phone'] = 'Please enter a valid phone number'
        if not doctor:
            errors['doctor'] = 'Please select a doctor'
        if not date:
            errors['date'] = 'Please select a valid future date'
        else:
            try:
                appt_date = datetime.strptime(date, '%Y-%m-%d').date()
                if appt_date < datetime.now().date():
                    errors['date'] = 'Please select a future date'
            except ValueError:
                errors['date'] = 'Invalid date format'
        if not time:
            errors['time'] = 'Please select a time slot'
        if not reason:
            errors['reason'] = 'Please provide a reason for your visit'
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        appointment = Appointment(
            user_id=user.id,
            fullname=fullname,
            email=email,
            phone=phone,
            doctor=doctor,
            date=appt_date,
            time=time,
            reason=reason
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Appointment booked successfully!'})
    return render_template('appointment.html', user=user)

@app.route('/appointments', methods=['GET'])
def get_appointments():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    user_id = session['user_id']
    appointments = Appointment.query.filter_by(user_id=user_id).all()
    appointments_data = [{
        'id': appt.id,
        'fullname': appt.fullname,
        'email': appt.email,
        'phone': appt.phone,
        'doctor': appt.doctor,
        'doctorValue': appt.doctor.lower().replace(' ', '-'),
        'date': appt.date.strftime('%Y-%m-%d'),
        'time': appt.time,
        'reason': appt.reason
    } for appt in appointments]
    return jsonify({'success': True, 'appointments': appointments_data})

@app.route('/appointment/reschedule/<int:id>', methods=['POST'])
def reschedule_appointment(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    appointment = Appointment.query.get_or_404(id)
    if appointment.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Appointment ready for rescheduling'})

@app.route('/appointment/cancel/<int:id>', methods=['POST'])
def cancel_appointment(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    appointment = Appointment.query.get_or_404(id)
    if appointment.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Appointment cancelled successfully!'})

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not all([name, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('register_page'))
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register_page'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register_page'))
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash('Registration successful! Welcome!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))

@app.route('/diabetes')
def diabetes():
    if 'user_id' not in session:
        flash('Please log in or register to access this page.', 'info')
        return redirect(url_for('login_page'))
    return render_template('diabetes.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        age = int(request.form['age'])
        gender = request.form['gender']
        glucose = float(request.form['glucose'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        errors = validate_inputs(age, glucose, weight, height)
        if errors:
            return jsonify({'error': ' '.join(errors)}), 400
        bmi = weight / (height ** 2)
        input_data = pd.DataFrame([{
            'Glucose': glucose,
            'Age': age,
            'BMI': bmi
        }])
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]
        prediction_label = 'Diabetic' if prediction == 1 else 'Non-Diabetic'
        diet_info = get_diet_recommendation(glucose)
        exercise_info = get_exercise_recommendation(age, weight, glucose, bmi)
        user = DiabetesUser(age=age, gender=gender, glucose=glucose, height=height, bmi=bmi, prediction=prediction_label)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'prediction': prediction_label,
            'sugar_category': diet_info['category'],
            'bmi': round(bmi, 2),
            'diet_recommendation': diet_info['diet'],
            'food_recommendations': diet_info['foods'],
            'exercise_recommendations': exercise_info
        })
    except ValueError:
        return jsonify({'error': 'Invalid input format. Please enter valid numbers.'}), 400

@app.route('/diabetes_history')
def diabetes_history():
    if 'user_id' not in session:
        flash('Please log in or register to access this page.', 'info')
        return redirect(url_for('login_page'))
    users = DiabetesUser.query.order_by(DiabetesUser.id.desc()).all()
    return render_template('history.html', users=users)

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the doctor dashboard.', 'info')
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    # Filter appointments for today (modify as needed for doctor-specific logic)
    appointments = Appointment.query.filter_by(date=date.today()).all()
    prescriptions = Prescription.query.all()
    return render_template('doctor_dashboard.html', appointments=appointments, prescriptions=prescriptions, user=user)

@app.route('/upload', methods=['POST'])
def upload_report():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if 'reportFile' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('doctor_dashboard'))
    file = request.files['reportFile']
    patient_name = request.form.get('patientName')
    report_type = request.form.get('reportType')
    appointment_id = request.form.get('appointmentId')
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('doctor_dashboard'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        prescription = Prescription(
            user_id=session['user_id'],
            appointment_id=appointment_id if appointment_id else None,
            patient_name=patient_name,
            report_type=report_type,
            file_path=file_path
        )
        db.session.add(prescription)
        db.session.commit()
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    else:
        flash('Invalid file type. Only PNG and PDF are allowed.', 'error')
        return redirect(url_for('doctor_dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)