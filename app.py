from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import sqlite3
import hashlib
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import uuid

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import pandas as pd
from io import BytesIO
import json
from datetime import datetime, timedelta
import calendar
from flask import send_file
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from threading import Thread

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'thulasitmk181@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'tbex lpqr rorf zvxc'     # Replace with your app password

app.config['TWILIO_ACCOUNT_SID'] = 'AC2845bd39bcac45ca0590402bc30b622f'
app.config['TWILIO_AUTH_TOKEN'] = '9b6f668020af4fc8547464eafc79b410'
app.config['TWILIO_WHATSAPP_FROM'] = '+12513561896'  # Twilio WhatsApp sandbox number

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def send_email_async(app, recipient_email, subject, html_body, attachment_data=None, attachment_name=None):
    """Send email asynchronously"""
    def send_async_email():
        with app.app_context():
            try:
                msg = MIMEMultipart('alternative')
                msg['From'] = app.config['MAIL_USERNAME']
                msg['To'] = recipient_email
                msg['Subject'] = subject
                
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
                
                if attachment_data and attachment_name:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(attachment_data)
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment_name}'
                    )
                    msg.attach(attachment)
                server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
                server.starttls()
                server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                server.send_message(msg)
                server.quit()
                
                print(f"Email sent successfully to {recipient_email}")
                
            except Exception as e:
                print(f"Failed to send email to {recipient_email}: {str(e)}")
    
    thread = Thread(target=send_async_email)
    thread.start()

def send_whatsapp_async(app, phone_number, message):
    def send_async_whatsapp():
        with app.app_context():
            try:
                from twilio.rest import Client
                
                client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
                if not phone_number.startswith('whatsapp:'):
                    formatted_number = f"whatsapp:{phone_number}"
                else:
                    formatted_number = phone_number
                
                message = client.messages.create(
                    body=message,
                    from_=app.config['TWILIO_WHATSAPP_FROM'],
                    to=formatted_number
                )
                
                print(f"WhatsApp message sent successfully to {phone_number}: {message.sid}")
                
            except Exception as e:
                print(f"Failed to send WhatsApp message to {phone_number}: {str(e)}")
    
    thread = Thread(target=send_async_whatsapp)
    thread.start()

def generate_booking_confirmation_email(booking_data, car_data, user_data):
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8fafc; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .booking-details {{ background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .detail-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }}
            .detail-label {{ font-weight: bold; color: #4a5568; }}
            .detail-value {{ color: #2d3748; }}
            .car-info {{ background-color: #667eea; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .total-amount {{ background-color: #28a745; color: white; padding: 15px; border-radius: 8px; text-align: center; font-size: 18px; font-weight: bold; }}
            .footer {{ background-color: #2d3748; color: white; padding: 20px; text-align: center; }}
            .btn {{ display: inline-block; background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 Booking Confirmed!</h1>
                <p>Thank you for choosing CarBooking System</p>
            </div>
            
            <div class="content">
                <h2>Hello {user_data['username']}!</h2>
                <p>Your car booking has been confirmed successfully. Here are your booking details:</p>
                
                <div class="car-info">
                    <h3>🚙 {car_data['name']}</h3>
                    <p>{car_data['brand']} {car_data['model']} ({car_data['year']})</p>
                    <p>{car_data['description']}</p>
                </div>
                
                <div class="booking-details">
                    <h3>📋 Booking Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Booking ID:</span>
                        <span class="detail-value">#{booking_data['id']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Payment ID:</span>
                        <span class="detail-value">{booking_data['payment_id']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Start Date:</span>
                        <span class="detail-value">{booking_data['start_date']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">End Date:</span>
                        <span class="detail-value">{booking_data['end_date']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Duration:</span>
                        <span class="detail-value">{booking_data['days']} days</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Daily Rate:</span>
                        <span class="detail-value">${car_data['price_per_day']:.2f}</span>
                    </div>
                </div>
                
                <div class="total-amount">
                    💰 Total Amount: ₹{booking_data['total_amount']:.2f}
                </div>
                
                <h3>📍 Pickup Instructions</h3>
                <p>Please arrive at our location 15 minutes before your pickup time:</p>
                <ul>
                    <li><strong>Address:</strong> 5/192b Dharapuram Tirupur </li>
                    <li><strong>Phone:</strong> +91 7305371881</li>
                    <li><strong>Hours:</strong> 8:00 AM - 8:00 PM</li>
                </ul>
                
                <h3>📄 Required Documents</h3>
                <ul>
                    <li>Valid Driver's License</li>
                    <li>Credit Card for security deposit</li>
                    <li>Proof of Insurance (if applicable)</li>
                </ul>
                
                <p>If you have any questions or need to modify your booking, please contact us immediately.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:5000/my_bookings" class="btn">View My Bookings</a>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>DRIVEZX CarBooking</strong></p>
                <p>📧 drivezx@gmail.com, | 📞 +91 7305371881</p>
                <p>Thank you for choosing us for your transportation needs!</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

def generate_whatsapp_message(booking_data, car_data, user_data):
    """Generate WhatsApp message for booking confirmation"""
    message = f"""
🚗 *CarBooking Confirmation*

Hello {user_data['username']}! 

Your booking has been confirmed ✅

*Car Details:*
🚙 {car_data['name']}
📅 {booking_data['start_date']} to {booking_data['end_date']}
💰 Total:₹{booking_data['total_amount']:.2f}
🆔 Booking ID: #{booking_data['id']}

*Pickup Location:*
📍 5/192B dharapuram Tirupur
📞 +91 7305371881

*Required Documents:*
• Valid Driver's License
• Credit Card
• Proof of Insurance

Questions? Reply to this message or call us!

Thank you for choosing CarBooking! 🙏
    """
    return message.strip()

def init_db():
    conn = sqlite3.connect('car_booking.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN address TEXT')
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price_per_day REAL NOT NULL,
            image_url TEXT,
            status TEXT DEFAULT 'available',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            next_service_date DATE,
            last_service_date DATE,
            service_notes TEXT
        )
    ''')

    try:
        cursor.execute('ALTER TABLE cars ADD COLUMN next_service_date DATE')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE cars ADD COLUMN last_service_date DATE')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE cars ADD COLUMN service_notes TEXT')
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_amount REAL NOT NULL,
            payment_id TEXT,
            status TEXT DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (car_id) REFERENCES cars (id)
        )
    ''')
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password, phone, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'thulasitmk181@gmail.com', admin_password, '+917305371881', 'admin'))

    cursor.execute('SELECT COUNT(*) FROM cars')
    if cursor.fetchone()[0] == 0:
        sample_cars = [
            ('Toyota Camry', 'Toyota', 'Camry', 2023, 50.0, 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=500', 'available', 'Comfortable sedan perfect for city drives', None, None, None),
            ('Honda Civic', 'Honda', 'Civic', 2022, 45.0, 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=500', 'available', 'Reliable and fuel-efficient compact car', None, None, None),
            ('BMW X5', 'BMW', 'X5', 2023, 120.0, 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=500', 'available', 'Luxury SUV with premium features', None, None, None),
            ('Mercedes C-Class', 'Mercedes', 'C-Class', 2023, 100.0, 'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500', 'available', 'Elegant luxury sedan', None, None, None),
            ('Ford Mustang', 'Ford', 'Mustang', 2022, 80.0, 'https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=500', 'available', 'Powerful sports car for thrill seekers', None, None, None),
            ('Audi A4', 'Audi', 'A4', 2023, 90000.0, 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=500', 'available', 'Premium sedan with advanced technology',None,None,None),
('Volkswagen Golf', 'Volkswagen', 'Golf', 2022, 5000, 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=500', 'available', 'Compact hatchback perfect for urban driving',None,None,None),
('Chevrolet Malibu', 'Chevrolet', 'Malibu', 2023, 5500, 'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=500', 'available', 'Spacious midsize sedan with modern features',None,None,None)

        ]
        
        cursor.executemany('''
            INSERT INTO cars (name, brand, model, year, price_per_day, image_url, status, description, next_service_date, last_service_date, service_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_cars)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('car_booking.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars WHERE status = "available" LIMIT 6').fetchall()
    conn.close()
    return render_template('index.html', cars=cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form.get('phone', '')
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (username, email, phone, password)
                VALUES (?, ?, ?, ?)
            ''', (username, email, phone, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        user = conn.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, hashed_password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome back, {user["username"]}!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/cars')
def cars():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars WHERE status = "available"').fetchall()
    conn.close()
    return render_template('cars.html', cars=cars)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (car_id,)).fetchone()
    conn.close()
    
    if not car:
        flash('Car not found!', 'error')
        return redirect(url_for('cars'))
    
    return render_template('car_detail.html', car=car)

@app.route('/book/<int:car_id>', methods=['GET', 'POST'])
@login_required
def book_car(car_id):
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ? AND status = "available"', (car_id,)).fetchone()
    
    if not car:
        flash('Car not available for booking!', 'error')
        return redirect(url_for('cars'))
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end - start).days + 1
        total_amount = days * car['price_per_day']

        session['booking_details'] = {
            'car_id': car_id,
            'start_date': start_date,
            'end_date': end_date,
            'total_amount': total_amount,
            'days': days
        }
        
        conn.close()
        return redirect(url_for('payment'))
    
    conn.close()
    return render_template('book_car.html', car=car)

@app.route('/payment')
@login_required
def payment():
    if 'booking_details' not in session:
        flash('No booking details found!', 'error')
        return redirect(url_for('cars'))
    
    booking_details = session['booking_details']
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (booking_details['car_id'],)).fetchone()
    conn.close()
    
    return render_template('payment.html', car=car, booking=booking_details)

@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    if 'booking_details' not in session:
        flash('No booking details found!', 'error')
        return redirect(url_for('cars'))
    
    booking_details = session['booking_details']
    payment_id = f"pay_{uuid.uuid4().hex[:12]}"
    
    conn = get_db_connection()

    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (booking_details['car_id'],)).fetchone()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (user_id, car_id, start_date, end_date, total_amount, payment_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        session['user_id'],
        booking_details['car_id'],
        booking_details['start_date'],
        booking_details['end_date'],
        booking_details['total_amount'],
        payment_id,
        'confirmed'
    ))
    
    booking_id = cursor.lastrowid

    conn.execute('UPDATE cars SET status = "rented" WHERE id = ?', (booking_details['car_id'],))
    
    conn.commit()
    booking_data = {
        'id': booking_id,
        'payment_id': payment_id,
        'start_date': booking_details['start_date'],
        'end_date': booking_details['end_date'],
        'total_amount': booking_details['total_amount'],
        'days': booking_details['days']
    }
    
    user_data = {
        'username': user['username'],
        'email': user['email'],
        'phone': user['phone']
    }
    
    car_data = {
        'name': car['name'],
        'brand': car['brand'],
        'model': car['model'],
        'year': car['year'],
        'price_per_day': car['price_per_day'],
        'description': car['description']
    }

    if user['email']:
        email_subject = f"🚗 Booking Confirmed - {car['name']} (#{booking_id})"
        email_body = generate_booking_confirmation_email(booking_data, car_data, user_data)
        send_email_async(app, user['email'], email_subject, email_body)

    if user['phone']:
        whatsapp_message = generate_whatsapp_message(booking_data, car_data, user_data)
        send_whatsapp_async(app, user['phone'], whatsapp_message)
    
    conn.close()
    session.pop('booking_details', None)
    
    flash('Payment successful! Your booking has been confirmed. Check your email and WhatsApp for confirmation details.', 'success')
    return redirect(url_for('my_bookings'))

@app.route('/my_bookings')
@login_required
def my_bookings():
    conn = get_db_connection()
    bookings = conn.execute('''
        SELECT b.*, c.name as car_name, c.brand, c.model, c.image_url
        FROM bookings b
        JOIN cars c ON b.car_id = c.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    conn = get_db_connection()
    booking = conn.execute('''
        SELECT b.*, u.username, u.email, u.phone, c.name as car_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN cars c ON b.car_id = c.id
        WHERE b.id = ? AND b.user_id = ?
    ''', (booking_id, session['user_id'])).fetchone()
    
    if not booking:
        flash('Booking not found!', 'error')
        return redirect(url_for('my_bookings'))
    conn.execute('UPDATE bookings SET status = "cancelled" WHERE id = ?', (booking_id,))
    conn.execute('UPDATE cars SET status = "available" WHERE id = ?', (booking['car_id'],))
    
    conn.commit()
    conn.close()
    if booking['email']:
        email_subject = f"🚗 Booking Cancelled - {booking['car_name']} (#{booking_id})"
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                    <h1>❌ Booking Cancelled</h1>
                </div>
                
                <h2>Hello {booking['username']}!</h2>
                <p>Your booking has been successfully cancelled.</p>
                
                <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>Cancelled Booking Details:</h3>
                    <p><strong>Booking ID:</strong> #{booking_id}</p>
                    <p><strong>Car:</strong> {booking['car_name']}</p>
                    <p><strong>Dates:</strong> {booking['start_date']} to {booking['end_date']}</p>
                    <p><strong>Amount:</strong> ₹{booking['total_amount']:.2f}</p>
                </div>
                
                <p>If you have any questions about your cancellation or refund, please contact us.</p>
                
                <div style="background-color: #2d3748; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-top: 30px;">
                    <p><strong>DRIVEZX CarBooking</strong></p>
                    <p>📧 support@carbooking.com | 📞 +91 7305371881</p>
                </div>
            </div>
        </body>
        </html>
        """
        send_email_async(app, booking['email'], email_subject, email_body)
    
    if booking['phone']:
        whatsapp_message = f"""
🚗 *CarBooking Cancellation*

Hello {booking['username']}!

Your booking has been cancelled ❌

*Cancelled Booking:*
🆔 Booking ID: #{booking_id}
🚙 Car: {booking['car_name']}
📅 Dates: {booking['start_date']} to {booking['end_date']}
💰 Amount: ₹{booking['total_amount']:.2f}

Questions about refunds? Contact us:
📞 +91 7305371881
📧 support@carbooking.com

Thank you for using CarBooking! 🙏
        """
        send_whatsapp_async(app, booking['phone'], whatsapp_message.strip())
    
    flash('Booking cancelled successfully! Confirmation sent to your email and WhatsApp.', 'success')
    return redirect(url_for('my_bookings'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()

    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_cars = conn.execute('SELECT COUNT(*) FROM cars').fetchone()[0]
    total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
    rented_cars = conn.execute('SELECT COUNT(*) FROM cars WHERE status = "rented"').fetchone()[0]

    recent_bookings = conn.execute('''
        SELECT b.*, u.username, c.name as car_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN cars c ON b.car_id = c.id
        ORDER BY b.created_at DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    stats = {
        'total_users': total_users,
        'total_cars': total_cars,
        'total_bookings': total_bookings,
        'rented_cars': rented_cars
    }
    
    return render_template('admin_dashboard.html', stats=stats, recent_bookings=recent_bookings)

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/cars')
@admin_required
def admin_cars():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_cars.html', cars=cars)

@app.route('/admin/add_car', methods=['GET', 'POST'])
@admin_required
def add_car():
    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        model = request.form['model']
        year = int(request.form['year'])
        price_per_day = float(request.form['price_per_day'])
        description = request.form['description']
        image_url = request.form['image_url']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO cars (name, brand, model, year, price_per_day, image_url, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, brand, model, year, price_per_day, image_url, description))
        conn.commit()
        conn.close()
        
        flash('Car added successfully!', 'success')
        return redirect(url_for('admin_cars'))
    
    return render_template('add_car.html')

@app.route('/admin/edit_car/<int:car_id>', methods=['GET', 'POST'])
@admin_required
def edit_car(car_id):
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (car_id,)).fetchone()
    
    if not car:
        flash('Car not found!', 'error')
        return redirect(url_for('admin_cars'))
    
    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        model = request.form['model']
        year = int(request.form['year'])
        price_per_day = float(request.form['price_per_day'])
        description = request.form['description']
        image_url = request.form['image_url']
        status = request.form['status']
        
        conn.execute('''
            UPDATE cars SET name = ?, brand = ?, model = ?, year = ?, 
            price_per_day = ?, image_url = ?, description = ?, status = ?
            WHERE id = ?
        ''', (name, brand, model, year, price_per_day, image_url, description, status, car_id))
        conn.commit()
        conn.close()
        
        flash('Car updated successfully!', 'success')
        return redirect(url_for('admin_cars'))
    
    conn.close()
    return render_template('edit_car.html', car=car)

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    conn = get_db_connection()
    bookings = conn.execute('''
        SELECT b.*, u.username, c.name as car_name, c.brand, c.model
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN cars c ON b.car_id = c.id
        ORDER BY b.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin_bookings.html', bookings=bookings)

@app.route('/download_invoice/<int:booking_id>')
@login_required
def download_invoice(booking_id):
    conn = get_db_connection()
    if session.get('role') == 'admin':
        booking = conn.execute('''
            SELECT b.*, u.username, u.email, c.name as car_name, c.brand, c.model, c.year
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN cars c ON b.car_id = c.id
            WHERE b.id = ?
        ''', (booking_id,)).fetchone()
    else:
        booking = conn.execute('''
            SELECT b.*, u.username, u.email, c.name as car_name, c.brand, c.model, c.year
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN cars c ON b.car_id = c.id
            WHERE b.id = ? AND b.user_id = ?
        ''', (booking_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if not booking:
        flash('Booking not found!', 'error')
        return redirect(url_for('my_bookings'))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#667eea')
    )
    story.append(Paragraph("BOOKING INVOICE", title_style))
    story.append(Spacer(1, 20))
    company_info = [
        ["DRIVEZX TMK CARZ", ""],
        ["5/192B DHARAPURAM ", f"Invoice #: INV-{booking['id']:06d}"],
        ["TIRUPUR, TAMILNADU 638656", f"Date: {datetime.now().strftime('%B %d, %Y')}"],
        ["Phone: +91 7305371881", f"Payment ID: {booking['payment_id']}"]
    ]
    
    company_table = Table(company_info, colWidths=[3*inch, 3*inch])
    company_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(company_table)
\
    story.append(Paragraph("BILL TO:", styles['Heading3']))
    customer_info = [
        [f"Name: {booking['username']}"],
        [f"Email: {booking['email']}"],
        [f"Booking Date: {booking['created_at']}"]
    ]
    
    customer_table = Table(customer_info, colWidths=[6*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 30))
\
    start_date = datetime.strptime(booking['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(booking['end_date'], '%Y-%m-%d')
    days = (end_date - start_date).days + 1
    daily_rate = booking['total_amount'] / days
    
    booking_data = [
        ['Description', 'Start Date', 'End Date', 'Days', 'Rate/Day', 'Total'],
        [f"{booking['car_name']} ({booking['brand']} {booking['model']} {booking['year']})", 
         booking['start_date'], booking['end_date'], str(days), 
         f"₹{daily_rate:.2f}", f"₹{booking['total_amount']:.2f}"]
    ]
    
    booking_table = Table(booking_data, colWidths=[2.5*inch, 1*inch, 1*inch, 0.7*inch, 1*inch, 1*inch])
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(booking_table)
    story.append(Spacer(1, 30))
    total_data = [
        ['', '', '', '', 'TOTAL:', f"{booking['total_amount']:.2f}"]
    ]
    total_table = Table(total_data, colWidths=[2.5*inch, 1*inch, 1*inch, 0.7*inch, 1*inch, 1*inch])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (4, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (4, 0), (-1, -1), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (4, 0), (-1, -1), colors.whitesmoke),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 50))
    
    # Footer
    footer_text = "Thank you for choosing DRIVEZX CarBooking! For support, contact us at support@carbooking.com"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'invoice_{booking_id}.pdf',
        mimetype='application/pdf'
    )
@app.route('/admin/send_test_notification', methods=['POST'])
@admin_required
def send_test_notification():
    data = request.get_json()
    user_id = data.get('user_id')
    email = data.get('email')
    phone = data.get('phone')

    try:

        subject = "🔔 Test Notification"
        html_body = f"""
        <html>
        <body>
            <h2>Hello!</h2>
            <p>This is a <strong>test notification</strong> from the DRIVEZX Car Booking System admin panel.</p>
        </body>
        </html>
        """
        whatsapp_message = "🔔 This is a *test notification* from Car Booking System Admin Panel."

        if email:
            send_email_async(app, email, subject, html_body)
        if phone:
            send_whatsapp_async(app, phone, whatsapp_message)

        return jsonify(success=True, message="Notification sent")
    
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/export_bookings')
@admin_required
def export_bookings():
    format_type = request.args.get('format', 'excel')
    
    conn = get_db_connection()
    bookings = conn.execute('''
        SELECT b.id, u.username, u.email, c.name as car_name, c.brand, c.model,
               b.start_date, b.end_date, b.total_amount, b.payment_id, b.status, b.created_at
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN cars c ON b.car_id = c.id
        ORDER BY b.created_at DESC
    ''').fetchall()
    conn.close()
    
    if format_type == 'excel':
        df = pd.DataFrame([dict(booking) for booking in bookings])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Bookings', index=False)
        
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'bookings_export_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    else: 
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.HexColor('#667eea')
        )
        story.append(Paragraph("BOOKINGS REPORT", title_style))
        story.append(Spacer(1, 20))
        data = [['ID', 'User', 'Car', 'Start Date', 'End Date', 'Amount', 'Status']]
        for booking in bookings:
            data.append([
                str(booking['id']),
                booking['username'],
                f"{booking['car_name']} ({booking['brand']})",
                booking['start_date'],
                booking['end_date'],
                f"₹{booking['total_amount']:.2f}",
                booking['status'].title()
            ])
        
        table = Table(data, colWidths=[0.5*inch, 1*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'bookings_report_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )

@app.route('/api/analytics')
@admin_required
def analytics_api():
    conn = get_db_connection()
    bookings_per_month = []
    revenue_per_month = []
    
    for i in range(12):
        date = datetime.now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        next_month = month_start.replace(month=month_start.month % 12 + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
        
        bookings = conn.execute('''
            SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as revenue
            FROM bookings 
            WHERE created_at >= ? AND created_at < ?
        ''', (month_start.strftime('%Y-%m-%d'), next_month.strftime('%Y-%m-%d'))).fetchone()
        
        bookings_per_month.append({
            'month': month_start.strftime('%b %Y'),
            'bookings': bookings['count']
        })
        
        revenue_per_month.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(bookings['revenue'])
        })

    most_rented = conn.execute('''
        SELECT c.name, c.brand, c.model, COUNT(b.id) as bookings
        FROM cars c
        LEFT JOIN bookings b ON c.id = b.car_id
        GROUP BY c.id
        ORDER BY bookings DESC
        LIMIT 10
    ''').fetchall()

    car_status = conn.execute('''
        SELECT status, COUNT(*) as count
        FROM cars
        GROUP BY status
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'bookings_per_month': list(reversed(bookings_per_month)),
        'revenue_per_month': list(reversed(revenue_per_month)),
        'most_rented': [dict(car) for car in most_rented],
        'car_status': [dict(status) for status in car_status]
    })
@app.route('/admin/profile')
@admin_required
def admin_profile():
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if admin and isinstance(admin['created_at'], str):
        try:
            admin = dict(admin)
            admin['created_at'] = datetime.strptime(admin['created_at'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            admin['created_at'] = None  # fallback if format is invalid

    return render_template('admin_profile.html', user=admin)
@app.route('/admin/update_profile', methods=['GET', 'POST'])
@admin_required
def admin_update_profile():
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')

        conn.execute('UPDATE users SET username = ?, email = ?, phone = ? WHERE id = ?', 
                     (name, email, phone, session['user_id']))
        conn.commit()
        conn.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin_profile'))

    conn.close()
    return render_template('admin_update_profile.html', user=admin)
@app.route('/admin/change_password', methods=['GET', 'POST'])
@admin_required
def admin_change_password():
    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()

        current_hashed = hashlib.sha256(current.encode()).hexdigest()

        if current_hashed != admin['password']:
            flash('Current password is incorrect!', 'danger')
        elif new != confirm:
            flash('New passwords do not match!', 'danger')
        else:
            new_hashed = hashlib.sha256(new.encode()).hexdigest()
            conn = get_db_connection()
            conn.execute('UPDATE users SET password = ? WHERE id = ?', (new_hashed, session['user_id']))
            conn.commit()
            conn.close()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('admin_profile'))

    return render_template('admin_change_password.html')

from datetime import datetime

@app.route('/user/profile')
@login_required
def user_profile():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if user and isinstance(user['created_at'], str):
        try:
            user = dict(user)
            user['created_at'] = datetime.strptime(user['created_at'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            user['created_at'] = None  # fallback if format is unexpected

    return render_template('user_profile.html', user=user)

@app.route('/user/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')
        address = request.form.get('address')

        conn.execute('UPDATE users SET username = ?, email = ?, phone = ?, address = ? WHERE id = ?', 
                     (name, email, phone, address, session['user_id']))
        conn.commit()
        conn.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))

    conn.close()
    return render_template('update_profile.html', user=user)
@app.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()

        current_hashed = hashlib.sha256(current.encode()).hexdigest()

        if current_hashed != user['password']:
            flash('Current password is incorrect!', 'danger')
        elif new != confirm:
            flash('New passwords do not match!', 'danger')
        else:
            new_hashed = hashlib.sha256(new.encode()).hexdigest()
            conn = get_db_connection()
            conn.execute('UPDATE users SET password = ? WHERE id = ?', (new_hashed, session['user_id']))
            conn.commit()
            conn.close()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('user_profile'))

    return render_template('change_password.html')

@app.route('/admin/maintenance')
@admin_required
def admin_maintenance():
    conn = get_db_connection()
    cars = conn.execute('''
        SELECT *, 
        CASE 
            WHEN next_service_date IS NOT NULL AND next_service_date <= date('now') 
            THEN 'overdue'
            WHEN next_service_date IS NOT NULL AND next_service_date <= date('now', '+7 days')
            THEN 'due_soon'
            ELSE 'ok'
        END as service_status
        FROM cars 
        ORDER BY next_service_date ASC
    ''').fetchall()
    conn.close()
    return render_template('admin_maintenance.html', cars=cars)
@app.route('/notification-settings', methods=['GET', 'POST'])
def notification_settings():
    user = None
    if 'user_id' in session:
        conn = sqlite3.connect('car_booking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone FROM users WHERE id = ?", (session['user_id'],))
        row = cursor.fetchone()
        conn.close()
        if row:
            user = {'phone': row[0]}

    if request.method == 'POST':
        flash("Notification preferences updated!", "success")
    
    return render_template('notification_settings.html', user=user)
@app.route('/admin/update_maintenance/<int:car_id>', methods=['POST'])
@admin_required
def update_maintenance(car_id):
    next_service_date = request.form['next_service_date']
    last_service_date = request.form.get('last_service_date')
    service_notes = request.form.get('service_notes', '')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE cars 
        SET next_service_date = ?, last_service_date = ?, service_notes = ?
        WHERE id = ?
    ''', (next_service_date, last_service_date, service_notes, car_id))
    conn.commit()
    conn.close()
    
    flash('Maintenance schedule updated successfully!', 'success')
    return redirect(url_for('admin_maintenance'))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return render_template('admin_analytics.html')

@app.route('/car_locations')
def car_locations():
    return render_template('car_locations.html')

@app.route('/chat_support')
def chat_support():
    return render_template('chat_support.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
