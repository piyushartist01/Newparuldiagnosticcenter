"""Main Flask application for New Parul Diagnostic Center."""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt

from config import Config
from models import db, AdminUser, Service


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
                static_url_path='/static')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Enable CORS for the desktop admin app
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Register blueprint
    from routes import api
    app.register_blueprint(api)

    # Apply stricter rate limits to public form submission endpoints
    limiter.limit("10 per hour")(api)

    # -----------------------------------------------------------------------
    # Serve the frontend SPA
    # -----------------------------------------------------------------------
    @app.route('/')
    def serve_index():
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        return send_from_directory(os.path.abspath(frontend_dir), 'index.html')

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'assets')
        return send_from_directory(os.path.abspath(assets_dir), filename)

    # -----------------------------------------------------------------------
    # Seed default data on first run
    # -----------------------------------------------------------------------
    with app.app_context():
        db.create_all()
        _seed_defaults(app)

    return app


def _seed_defaults(app):
    """Create default admin user and services if they don't exist."""
    # Default admin
    if AdminUser.query.count() == 0:
        pw = app.config['ADMIN_PASSWORD']
        hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = AdminUser(
            username=app.config['ADMIN_USERNAME'],
            password_hash=hashed,
            email=app.config['ADMIN_EMAIL']
        )
        db.session.add(admin)
        app.logger.info(f"Default admin user created: {app.config['ADMIN_USERNAME']}")

    # Default services
    if Service.query.count() == 0:
        default_services = [
            Service(service_name='Complete Blood Count (CBC)',
                    description='A comprehensive blood test that measures red blood cells, white blood cells, hemoglobin, hematocrit, and platelets.',
                    price=350),
            Service(service_name='Blood Sugar (Fasting / PP)',
                    description='Measures blood glucose levels to screen for diabetes and monitor blood sugar control.',
                    price=150),
            Service(service_name='Lipid Profile',
                    description='Measures cholesterol levels including HDL, LDL, triglycerides, and total cholesterol.',
                    price=500),
            Service(service_name='Thyroid Profile (T3, T4, TSH)',
                    description='Evaluates thyroid gland function by measuring thyroid hormone levels.',
                    price=600),
            Service(service_name='Liver Function Test (LFT)',
                    description='Assesses liver health by measuring enzymes, proteins, and bilirubin levels.',
                    price=550),
            Service(service_name='Kidney Function Test (KFT)',
                    description='Evaluates kidney health by measuring creatinine, BUN, and electrolytes.',
                    price=550),
            Service(service_name='Urine Analysis',
                    description='Complete urine examination to detect infections, kidney disorders, and other conditions.',
                    price=200),
            Service(service_name='X-Ray',
                    description='Diagnostic imaging to examine bones, chest, and other body parts for abnormalities.',
                    price=400),
            Service(service_name='ECG (Electrocardiogram)',
                    description='Records the electrical activity of the heart to detect cardiac conditions.',
                    price=300),
            Service(service_name='Ultrasound',
                    description='Non-invasive imaging using sound waves to examine internal organs and tissues.',
                    price=800),
            Service(service_name='Vitamin D Test',
                    description='Measures vitamin D levels in the blood to assess deficiency or excess.',
                    price=700),
            Service(service_name='HbA1c (Glycated Hemoglobin)',
                    description='Measures average blood sugar over the past 2-3 months for diabetes management.',
                    price=450),
        ]
        db.session.add_all(default_services)
        app.logger.info("Default services seeded")

    db.session.commit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
