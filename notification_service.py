"""
Notification Service Module
Handles email and WhatsApp messaging functionality
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from threading import Thread
from datetime import datetime, timedelta

class NotificationService:
    def __init__(self, app):
        self.app = app
        
    def send_email_async(self, recipient_email, subject, html_body, attachment_data=None, attachment_name=None):
        """Send email asynchronously"""
        def send_async_email():
            with self.app.app_context():
                try:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = self.app.config['MAIL_USERNAME']
                    msg['To'] = recipient_email
                    msg['Subject'] = subject
                    
                    # Add HTML body
                    html_part = MIMEText(html_body, 'html')
                    msg.attach(html_part)
                    
                    # Add attachment if provided
                    if attachment_data and attachment_name:
                        attachment = MIMEBase('application', 'octet-stream')
                        attachment.set_payload(attachment_data)
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment_name}'
                        )
                        msg.attach(attachment)
                    
                    # Send email
                    server = smtplib.SMTP(self.app.config['MAIL_SERVER'], self.app.config['MAIL_PORT'])
                    server.starttls()
                    server.login(self.app.config['MAIL_USERNAME'], self.app.config['MAIL_PASSWORD'])
                    server.send_message(msg)
                    server.quit()
                    
                    print(f"Email sent successfully to {recipient_email}")
                    return True
                    
                except Exception as e:
                    print(f"Failed to send email to {recipient_email}: {str(e)}")
                    return False
        
        thread = Thread(target=send_async_email)
        thread.start()
        return thread

    def send_whatsapp_async(self, phone_number, message):
        """Send WhatsApp message asynchronously using Twilio"""
        def send_async_whatsapp():
            with self.app.app_context():
                try:
                    from twilio.rest import Client
                    
                    client = Client(self.app.config['TWILIO_ACCOUNT_SID'], self.app.config['TWILIO_AUTH_TOKEN'])
                    
                    # Format phone number for WhatsApp
                    if not phone_number.startswith('whatsapp:'):
                        formatted_number = f"whatsapp:{phone_number}"
                    else:
                        formatted_number = phone_number
                    
                    message_obj = client.messages.create(
                        body=message,
                        from_=self.app.config['TWILIO_WHATSAPP_FROM'],
                        to=formatted_number
                    )
                    
                    print(f"WhatsApp message sent successfully to {phone_number}: {message_obj.sid}")
                    return True
                    
                except Exception as e:
                    print(f"Failed to send WhatsApp message to {phone_number}: {str(e)}")
                    return False
        
        thread = Thread(target=send_async_whatsapp)
        thread.start()
        return thread

    def send_booking_reminder(self, booking_data, user_data, car_data, hours_before=24):
        """Send booking reminder notifications"""
        # Email reminder
        if user_data.get('email'):
            subject = f"🚗 Reminder: Your car pickup is in {hours_before} hours - {car_data['name']}"
            html_body = self.generate_reminder_email(booking_data, user_data, car_data, hours_before)
            self.send_email_async(user_data['email'], subject, html_body)
        
        # WhatsApp reminder
        if user_data.get('phone'):
            message = self.generate_reminder_whatsapp(booking_data, user_data, car_data, hours_before)
            self.send_whatsapp_async(user_data['phone'], message)

    def generate_reminder_email(self, booking_data, user_data, car_data, hours_before):

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(135deg, #ffc107 0%, #ff8f00 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .reminder-box {{ background-color: #fff3cd; border: 2px solid #ffc107; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .car-info {{ background-color: #667eea; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .checklist {{ background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background-color: #2d3748; color: white; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Pickup Reminder</h1>
                    <p>Your car rental is coming up soon!</p>
                </div>
                
                <div class="content">
                    <div class="reminder-box">
                        <h2>🚨 {hours_before} Hours Until Pickup!</h2>
                        <p><strong>Pickup Date:</strong> {booking_data['start_date']}</p>
                        <p><strong>Booking ID:</strong> #{booking_data['id']}</p>
                    </div>
                    
                    <div class="car-info">
                        <h3>🚙 {car_data['name']}</h3>
                        <p>{car_data['brand']} {car_data['model']} ({car_data['year']})</p>
                    </div>
                    
                    <div class="checklist">
                        <h3>📋 Pickup Checklist</h3>
                        <ul style="text-align: left;">
                            <li>✅ Valid Driver's License</li>
                            <li>✅ Credit Card for security deposit</li>
                            <li>✅ Proof of Insurance (if applicable)</li>
                            <li>✅ Booking confirmation (this email)</li>
                        </ul>
                    </div>
                    
                    <h3>📍 Pickup Location</h3>
                    <p><strong>Address:</strong> 123 Main Street, City, State 12345</p>
                    <p><strong>Phone:</strong> (555) 123-4567</p>
                    <p><strong>Hours:</strong> 8:00 AM - 8:00 PM</p>
                </div>
                
                <div class="footer">
                    <p><strong>CarBooking System</strong></p>
                    <p>📧 support@carbooking.com | 📞 (555) 123-4567</p>
                </div>
            </div>
        </body>
        </html>
        """

    def generate_reminder_whatsapp(self, booking_data, user_data, car_data, hours_before):
        """Generate WhatsApp reminder message"""
        return f"""
⏰ *CarBooking Reminder*

Hello {user_data['username']}!

Your car pickup is in *{hours_before} hours*! 🚗

*Booking Details:*
🆔 ID: #{booking_data['id']}
🚙 Car: {car_data['name']}
📅 Pickup: {booking_data['start_date']}

*Don't forget to bring:*
• Valid Driver's License ✅
• Credit Card ✅
• Proof of Insurance ✅

*Pickup Location:*
📍 5/192b dharapuram , Tirupur,Tamilnadu
📞 +91 7305371881

See you soon! 🙏
        """.strip()
