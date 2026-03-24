"""API routes for New Parul Diagnostic Center.

Public endpoints for the frontend + JWT-protected admin API endpoints
consumed by the PyQt6 desktop admin application.
"""

import csv
import io
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
import bcrypt
from flask import Blueprint, request, jsonify, Response, current_app

from models import db, Appointment, Service, AdminUser, ContactMessage

# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------
api = Blueprint('api', __name__)


# ---------------------------------------------------------------------------
# JWT Helpers
# ---------------------------------------------------------------------------
def generate_token(user):
    """Create a JWT for the given admin user."""
    payload = {
        'sub': user.id,
        'username': user.username,
        'exp': datetime.now(timezone.utc) + timedelta(
            hours=current_app.config['JWT_EXPIRATION_HOURS']
        ),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """Decorator that enforces a valid JWT in the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            request.admin_user = AdminUser.query.get(payload['sub'])
            if request.admin_user is None:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def validate_email(email):
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Basic phone number validation (digits, spaces, +, -, parens)."""
    pattern = r'^[\d\s\+\-\(\)]{7,20}$'
    return re.match(pattern, phone) is not None


def send_email(to_email, subject, html_body):
    """Send an email using SMTP. Logs to console if credentials missing."""
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT')
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER')

    if not mail_username or not mail_password:
        current_app.logger.info(
            f"[EMAIL LOG] To: {to_email} | Subject: {subject}\n{html_body}"
        )
        return

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_sender
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.sendmail(mail_sender, to_email, msg.as_string())

        current_app.logger.info(f"Email sent to {to_email}")
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")


# ===========================================================================
# PUBLIC API ENDPOINTS
# ===========================================================================

@api.route('/api/services', methods=['GET'])
def get_services():
    """Fetch all available services."""
    services = Service.query.order_by(Service.service_name).all()
    return jsonify([s.to_dict() for s in services])


@api.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Book a new appointment."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    # Required fields
    required = ['patient_name', 'email', 'phone', 'appointment_date',
                 'appointment_time', 'service_type']
    missing = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email address'}), 400

    if not validate_phone(data['phone']):
        return jsonify({'error': 'Invalid phone number'}), 400

    # Validate date
    try:
        appt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        today = datetime.now(timezone.utc).date()
        if appt_date < today:
            return jsonify({'error': 'Appointment date cannot be in the past'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Validate time
    try:
        datetime.strptime(data['appointment_time'], '%H:%M')
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400

    appointment = Appointment(
        patient_name=data['patient_name'].strip(),
        email=data['email'].strip().lower(),
        phone=data['phone'].strip(),
        appointment_date=data['appointment_date'],
        appointment_time=data['appointment_time'],
        service_type=data['service_type'].strip(),
        notes=data.get('notes', '').strip(),
        status='pending'
    )
    db.session.add(appointment)
    db.session.commit()

    # Send confirmation email to patient
    send_email(
        appointment.email,
        'Appointment Confirmation – New Parul Diagnostic Center',
        f"""
        <h2>Appointment Confirmed!</h2>
        <p>Dear <strong>{appointment.patient_name}</strong>,</p>
        <p>Your appointment has been received successfully.</p>
        <table style="border-collapse:collapse;">
            <tr><td style="padding:4px 12px;font-weight:bold;">Service:</td><td>{appointment.service_type}</td></tr>
            <tr><td style="padding:4px 12px;font-weight:bold;">Date:</td><td>{appointment.appointment_date}</td></tr>
            <tr><td style="padding:4px 12px;font-weight:bold;">Time:</td><td>{appointment.appointment_time}</td></tr>
        </table>
        <p>We will contact you shortly to confirm your appointment.</p>
        <p>Thank you,<br>New Parul Diagnostic Center</p>
        """
    )

    # Notify admin
    admin_email = current_app.config.get('ADMIN_EMAIL', '')
    if admin_email:
        send_email(
            admin_email,
            'New Appointment Booking',
            f"<p>New appointment from <strong>{appointment.patient_name}</strong> "
            f"for <strong>{appointment.service_type}</strong> on "
            f"{appointment.appointment_date} at {appointment.appointment_time}.</p>"
        )

    return jsonify({
        'message': 'Appointment booked successfully!',
        'appointment': appointment.to_dict()
    }), 201


@api.route('/api/contact', methods=['POST'])
def submit_contact():
    """Submit a contact form message."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    required = ['name', 'email', 'message']
    missing = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email address'}), 400

    msg = ContactMessage(
        name=data['name'].strip(),
        email=data['email'].strip().lower(),
        message=data['message'].strip()
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully! We will get back to you soon.'}), 201


# ===========================================================================
# ADMIN API ENDPOINTS (JWT Protected)
# ===========================================================================

# ---- Authentication -------------------------------------------------------

@api.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Authenticate admin and return a JWT token."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = AdminUser.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        token = generate_token(user)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        })

    return jsonify({'error': 'Invalid username or password'}), 401


# ---- Dashboard ------------------------------------------------------------

@api.route('/api/admin/dashboard', methods=['GET'])
@token_required
def admin_dashboard():
    """Return dashboard statistics."""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    todays_appointments = Appointment.query.filter_by(appointment_date=today).count()
    pending = Appointment.query.filter_by(status='pending').count()
    confirmed = Appointment.query.filter_by(status='confirmed').count()
    completed = Appointment.query.filter_by(status='completed').count()
    total = Appointment.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()

    recent_appointments = Appointment.query.order_by(
        Appointment.created_at.desc()
    ).limit(10).all()

    recent_messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).limit(5).all()

    return jsonify({
        'todays_appointments': todays_appointments,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed,
        'total': total,
        'unread_messages': unread_messages,
        'recent_appointments': [a.to_dict() for a in recent_appointments],
        'recent_messages': [m.to_dict() for m in recent_messages],
    })


# ---- Appointments ---------------------------------------------------------

@api.route('/api/admin/appointments', methods=['GET'])
@token_required
def admin_appointments():
    """List all appointments with optional status filter."""
    status_filter = request.args.get('status', '')
    query = Appointment.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    appointments_list = query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify([a.to_dict() for a in appointments_list])


@api.route('/api/admin/appointments/<int:appt_id>', methods=['PUT'])
@token_required
def update_appointment(appt_id):
    """Update an appointment's status."""
    appt = Appointment.query.get_or_404(appt_id)
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    allowed = ['pending', 'confirmed', 'completed', 'cancelled']
    if data['status'] not in allowed:
        return jsonify({'error': f'Status must be one of: {", ".join(allowed)}'}), 400
    appt.status = data['status']
    db.session.commit()

    # Notify patient about status change
    send_email(
        appt.email,
        f'Appointment {appt.status.title()} – New Parul Diagnostic Center',
        f"""
        <p>Dear <strong>{appt.patient_name}</strong>,</p>
        <p>Your appointment for <strong>{appt.service_type}</strong> on
        {appt.appointment_date} at {appt.appointment_time} has been
        <strong>{appt.status}</strong>.</p>
        <p>Thank you,<br>New Parul Diagnostic Center</p>
        """
    )

    return jsonify({'message': 'Appointment updated', 'appointment': appt.to_dict()})


@api.route('/api/admin/appointments/<int:appt_id>', methods=['DELETE'])
@token_required
def delete_appointment(appt_id):
    """Delete an appointment."""
    appt = Appointment.query.get_or_404(appt_id)
    db.session.delete(appt)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted'})


# ---- Services -------------------------------------------------------------

@api.route('/api/admin/services', methods=['GET'])
@token_required
def admin_services():
    """List all services (admin view)."""
    services_list = Service.query.order_by(Service.service_name).all()
    return jsonify([s.to_dict() for s in services_list])


@api.route('/api/admin/services', methods=['POST'])
@token_required
def add_service():
    """Add a new service."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    name = data.get('service_name', '').strip()
    if not name:
        return jsonify({'error': 'Service name is required'}), 400

    desc = data.get('description', '').strip()
    try:
        price = float(data.get('price', 0))
    except (ValueError, TypeError):
        price = 0.0

    service = Service(service_name=name, description=desc, price=price)
    db.session.add(service)
    db.session.commit()
    return jsonify({'message': 'Service added', 'service': service.to_dict()}), 201


@api.route('/api/admin/services/<int:service_id>', methods=['PUT'])
@token_required
def edit_service(service_id):
    """Update an existing service."""
    service = Service.query.get_or_404(service_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    if 'service_name' in data:
        service.service_name = data['service_name'].strip()
    if 'description' in data:
        service.description = data['description'].strip()
    if 'price' in data:
        try:
            service.price = float(data['price'])
        except (ValueError, TypeError):
            pass

    db.session.commit()
    return jsonify({'message': 'Service updated', 'service': service.to_dict()})


@api.route('/api/admin/services/<int:service_id>', methods=['DELETE'])
@token_required
def delete_service(service_id):
    """Delete a service."""
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Service deleted'})


# ---- Messages -------------------------------------------------------------

@api.route('/api/admin/messages', methods=['GET'])
@token_required
def admin_messages():
    """List all contact messages."""
    msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify([m.to_dict() for m in msgs])


@api.route('/api/admin/messages/<int:msg_id>/read', methods=['PUT'])
@token_required
def mark_message_read(msg_id):
    """Mark a contact message as read."""
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'message': 'Marked as read'})


# ---- Export ----------------------------------------------------------------

@api.route('/api/admin/export/appointments', methods=['GET'])
@token_required
def export_appointments():
    """Export all appointments as CSV."""
    appointments_list = Appointment.query.order_by(
        Appointment.appointment_date.desc()
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Patient Name', 'Email', 'Phone', 'Date', 'Time',
                      'Service', 'Notes', 'Status', 'Created At'])
    for a in appointments_list:
        writer.writerow([
            a.id, a.patient_name, a.email, a.phone,
            a.appointment_date, a.appointment_time,
            a.service_type, a.notes, a.status,
            a.created_at.isoformat() if a.created_at else ''
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=appointments.csv'}
    )
