# New Parul Diagnostic Center

Professional medical diagnostic center website with appointment booking, contact forms, and a standalone desktop admin application.

## Project Structure

```
new-parul-diagnostic/
├── frontend/              # Static website (HTML/CSS/JS)
│   ├── index.html
│   ├── css/styles.css
│   └── js/main.js
├── backend/               # Flask API server
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── requirements.txt
│   └── .env.example
├── admin_app/             # PyQt6 Desktop Admin App
│   ├── main.py
│   ├── api_client.py
│   └── requirements.txt
├── README.md
└── .gitignore
```

## Quick Start

### 1. Backend (Flask API)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The server starts at **http://localhost:5000**. On first run it automatically:
- Creates the SQLite database
- Seeds 12 medical services
- Creates a default admin user (`admin` / `admin123`)

### 2. Website

Open **http://localhost:5000** in your browser. The Flask server serves the frontend automatically.

### 3. Desktop Admin App

```bash
cd admin_app
pip install -r requirements.txt
python main.py
```

Log in with `admin` / `admin123` (or your custom credentials from `.env`).

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key...` | Flask secret key |
| `JWT_SECRET_KEY` | (same as SECRET_KEY) | JWT signing key |
| `JWT_EXPIRATION_HOURS` | `24` | Token expiry |
| `ADMIN_USERNAME` | `admin` | Default admin username |
| `ADMIN_PASSWORD` | `admin123` | Default admin password |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server |
| `MAIL_USERNAME` | *(empty)* | SMTP username |
| `MAIL_PASSWORD` | *(empty)* | SMTP password |

## API Endpoints

### Public
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/services` | List all services |
| `POST` | `/api/appointments` | Book an appointment |
| `POST` | `/api/contact` | Submit contact message |

### Admin (JWT Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/admin/login` | Get JWT token |
| `GET` | `/api/admin/dashboard` | Dashboard stats |
| `GET` | `/api/admin/appointments` | List appointments |
| `PUT` | `/api/admin/appointments/<id>` | Update status |
| `DELETE` | `/api/admin/appointments/<id>` | Delete |
| `GET/POST` | `/api/admin/services` | List / Add |
| `PUT/DELETE` | `/api/admin/services/<id>` | Update / Delete |
| `GET` | `/api/admin/messages` | List messages |
| `PUT` | `/api/admin/messages/<id>/read` | Mark read |
| `GET` | `/api/admin/export/appointments` | CSV export |

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Inter font, scroll animations)
- **Backend**: Flask, SQLAlchemy, SQLite, PyJWT, bcrypt
- **Admin App**: PyQt6
