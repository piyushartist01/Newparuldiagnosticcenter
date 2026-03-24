"""API Client for the New Parul Diagnostic Center admin desktop app.

Handles JWT authentication and all API requests to the Flask backend.
"""

import requests


class ApiClient:
    """HTTP client with JWT token management for the admin API."""

    def __init__(self, base_url="https://newparul-backend.onrender.com"):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.user = None
        self.session = requests.Session()

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def login(self, username, password):
        """Authenticate with the backend and store the JWT token.

        Returns (success: bool, message: str).
        """
        try:
            resp = self.session.post(
                f"{self.base_url}/api/admin/login",
                json={"username": username, "password": password},
                timeout=10,
            )
            data = resp.json()

            if resp.ok:
                self.token = data["token"]
                self.user = data.get("user", {})
                return True, "Login successful"
            else:
                return False, data.get("error", "Login failed")
        except requests.ConnectionError:
            return False, "Cannot connect to the server. Is it running?"
        except Exception as e:
            return False, str(e)

    def logout(self):
        """Clear stored credentials."""
        self.token = None
        self.user = None

    @property
    def is_authenticated(self):
        return self.token is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _request(self, method, path, **kwargs):
        """Make a request and return (data, error)."""
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(
                method, url, headers=self._headers(), timeout=5, **kwargs
            )
            if resp.status_code == 401:
                self.token = None
                return None, "Session expired. Please log in again."
            if resp.status_code == 404:
                return None, "Resource not found."

            # CSV or other non-JSON responses
            content_type = resp.headers.get("Content-Type", "")
            if "text/csv" in content_type:
                return resp.text, None

            data = resp.json()
            if not resp.ok:
                return None, data.get("error", f"Error {resp.status_code}")
            return data, None

        except requests.ConnectionError:
            return None, "Cannot connect to the server."
        except Exception as e:
            return None, str(e)

    # ------------------------------------------------------------------
    # Public API helpers
    # ------------------------------------------------------------------
    def get(self, path):
        return self._request("GET", path)

    def post(self, path, json_data=None):
        return self._request("POST", path, json=json_data)

    def put(self, path, json_data=None):
        return self._request("PUT", path, json=json_data)

    def delete(self, path):
        return self._request("DELETE", path)

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------
    def get_dashboard(self):
        return self.get("/api/admin/dashboard")

    def get_appointments(self, status=""):
        path = "/api/admin/appointments"
        if status:
            path += f"?status={status}"
        return self.get(path)

    def update_appointment_status(self, appt_id, status):
        return self.put(f"/api/admin/appointments/{appt_id}", {"status": status})

    def delete_appointment(self, appt_id):
        return self.delete(f"/api/admin/appointments/{appt_id}")

    def get_services(self):
        return self.get("/api/admin/services")

    def add_service(self, name, description, price):
        return self.post("/api/admin/services", {
            "service_name": name,
            "description": description,
            "price": price,
        })

    def update_service(self, service_id, name, description, price):
        return self.put(f"/api/admin/services/{service_id}", {
            "service_name": name,
            "description": description,
            "price": price,
        })

    def delete_service(self, service_id):
        return self.delete(f"/api/admin/services/{service_id}")

    def get_messages(self):
        return self.get("/api/admin/messages")

    def mark_message_read(self, msg_id):
        return self.put(f"/api/admin/messages/{msg_id}/read")

    def export_appointments_csv(self):
        return self.get("/api/admin/export/appointments")
