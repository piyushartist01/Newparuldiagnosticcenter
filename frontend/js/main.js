/* ===================================================================
   NEW PARUL DIAGNOSTIC CENTER — Frontend JavaScript
   Theme toggle, navigation, form handling, API integration
   =================================================================== */

// ---------------------------------------------------------------
// Service Icon Mapping
// ---------------------------------------------------------------
const SERVICE_ICONS = {
    'blood': '🩸',
    'sugar': '🍬',
    'lipid': '❤️',
    'thyroid': '🦋',
    'liver': '🫁',
    'kidney': '🫘',
    'urine': '🧪',
    'x-ray': '☢️',
    'xray': '☢️',
    'ecg': '💓',
    'electro': '💓',
    'ultrasound': '📡',
    'vitamin': '☀️',
    'hba1c': '📊',
    'hemoglobin': '📊',
    'default': '🔬'
};

function getServiceIcon(serviceName) {
    const name = serviceName.toLowerCase();
    for (const [key, icon] of Object.entries(SERVICE_ICONS)) {
        if (name.includes(key)) return icon;
    }
    return SERVICE_ICONS.default;
}

// ---------------------------------------------------------------
// DOM Ready
// ---------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initScrollReveal();
    loadServices();
    initAppointmentForm();
    initContactForm();
    setMinDate();
});

// ---------------------------------------------------------------
// Navigation (Hamburger, Active Link, Scroll)
// ---------------------------------------------------------------
function initNavigation() {
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    if (!hamburger || !navLinks) return;
    const links = navLinks.querySelectorAll('a');

    // Hamburger toggle
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
        hamburger.setAttribute('aria-expanded',
            hamburger.classList.contains('active'));
    });

    // Close menu on link click
    links.forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
        });
    });

    // Active link on scroll
    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY + 100;
        sections.forEach(section => {
            const top = section.offsetTop;
            const height = section.offsetHeight;
            const id = section.getAttribute('id');
            const link = navLinks.querySelector(`a[href="#${id}"]`);
            if (link) {
                if (scrollY >= top && scrollY < top + height) {
                    links.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                }
            }
        });
    });
}

// ---------------------------------------------------------------
// Scroll Reveal Animation
// ---------------------------------------------------------------
function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

// ---------------------------------------------------------------
// Load Services from API
// ---------------------------------------------------------------
async function loadServices() {
    const grid = document.getElementById('servicesGrid');
    const dropdown = document.getElementById('serviceType');

    try {
        const resp = await fetch('https://newparul-backend.onrender.com/api/services');
        if (!resp.ok) throw new Error('Failed to fetch');
        const services = await resp.json();

        // Render cards
        grid.innerHTML = services.map(s => `
            <div class="service-card reveal">
                <div class="card-icon">${getServiceIcon(s.service_name)}</div>
                <h4>${escapeHTML(s.service_name)}</h4>
                <p>${escapeHTML(s.description)}</p>
                <div class="service-price">₹${s.price} <span>onwards</span></div>
            </div>
        `).join('');

        // Populate dropdown
        services.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.service_name;
            opt.textContent = `${s.service_name} — ₹${s.price}`;
            dropdown.appendChild(opt);
        });

        // Re-observe new cards
        initScrollReveal();
    } catch (err) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                <p>⚠️ Unable to load services. Please refresh the page.</p>
            </div>
        `;
        console.error('Error loading services:', err);
    }
}

// ---------------------------------------------------------------
// Set Minimum Date to Today
// ---------------------------------------------------------------
function setMinDate() {
    const dateInput = document.getElementById('appointmentDate');
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);
}

// ---------------------------------------------------------------
// Appointment Form
// ---------------------------------------------------------------
function initAppointmentForm() {
    const form = document.getElementById('appointmentForm');
    const btn = document.getElementById('appointmentSubmitBtn');

    const fields = [
        { id: 'patientName', validate: v => v.trim().length >= 2, errId: 'patientNameError' },
        { id: 'patientPhone', validate: v => /^[\d\s\+\-\(\)]{7,20}$/.test(v), errId: 'patientPhoneError' },
        { id: 'appointmentDate', validate: v => v !== '', errId: 'appointmentDateError' },
        { id: 'serviceType', validate: v => v !== '', errId: 'serviceTypeError' },
    ];

    fields.forEach(({ id, validate, errId }) => {
        const el = document.getElementById(id);
        el.addEventListener('blur', () => validateField(el, validate, errId));
        el.addEventListener('input', () => {
            if (el.classList.contains('error')) {
                validateField(el, validate, errId);
            }
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate all
        let valid = true;
        fields.forEach(({ id, validate, errId }) => {
            if (!validateField(document.getElementById(id), validate, errId)) {
                valid = false;
            }
        });
        if (!valid) return;

        // Submit
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Booking...';

        try {
            const resp = await fetch('https://newparul-backend.onrender.com/api/appointments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    patient_name: document.getElementById('patientName').value.trim(),
                    phone: document.getElementById('patientPhone').value.trim(),
                    appointment_date: document.getElementById('appointmentDate').value,
                    service_type: document.getElementById('serviceType').value
                })
            });

            const data = await resp.json();

            if (resp.ok) {
                showToast('success', '✅ ' + data.message);
                form.reset();
                // Clear validation states
                form.querySelectorAll('.form-control').forEach(fc => {
                    fc.classList.remove('success', 'error');
                });
                form.querySelectorAll('.error-message').forEach(em => {
                    em.classList.remove('visible');
                });
            } else {
                showToast('error', '❌ ' + (data.error || 'Something went wrong'));
            }
        } catch (err) {
            showToast('error', '❌ Network error. Please try again.');
            console.error('Appointment error:', err);
        } finally {
            btn.disabled = false;
            btn.innerHTML = 'Submit Request';
        }
    });
}

// ---------------------------------------------------------------
// Contact Form
// ---------------------------------------------------------------
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    const btn = document.getElementById('contactSubmitBtn');
    if (!btn) return;

    const fields = [
        { id: 'contactName', validate: v => v.trim().length >= 2, errId: 'contactNameError' },
        { id: 'contactEmail', validate: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), errId: 'contactEmailError' },
        { id: 'contactMessage', validate: v => v.trim().length >= 5, errId: 'contactMessageError' },
    ];

    fields.forEach(({ id, validate, errId }) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('blur', () => validateField(el, validate, errId));
        el.addEventListener('input', () => {
            if (el.classList.contains('error')) {
                validateField(el, validate, errId);
            }
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        let valid = true;
        fields.forEach(({ id, validate, errId }) => {
            if (!validateField(document.getElementById(id), validate, errId)) {
                valid = false;
            }
        });
        if (!valid) return;

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Sending...';

        try {
            const resp = await fetch('https://newparul-backend.onrender.com/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('contactName').value.trim(),
                    email: document.getElementById('contactEmail').value.trim(),
                    message: document.getElementById('contactMessage').value.trim()
                })
            });

            const data = await resp.json();

            if (resp.ok) {
                showToast('success', '✅ ' + data.message);
                form.reset();
                form.querySelectorAll('.form-control').forEach(fc => {
                    fc.classList.remove('success', 'error');
                });
                form.querySelectorAll('.error-message').forEach(em => {
                    em.classList.remove('visible');
                });
            } else {
                showToast('error', '❌ ' + (data.error || 'Something went wrong'));
            }
        } catch (err) {
            showToast('error', '❌ Network error. Please try again.');
            console.error('Contact error:', err);
        } finally {
            btn.disabled = false;
            btn.innerHTML = 'Send Message';
        }
    });
}

// ---------------------------------------------------------------
// Utility: Field Validation
// ---------------------------------------------------------------
function validateField(el, validateFn, errorId) {
    const err = document.getElementById(errorId);
    if (validateFn(el.value)) {
        el.classList.remove('error');
        el.classList.add('success');
        err.classList.remove('visible');
        return true;
    } else {
        el.classList.remove('success');
        el.classList.add('error');
        err.classList.add('visible');
        return false;
    }
}

// ---------------------------------------------------------------
// Utility: Toast Notifications
// ---------------------------------------------------------------
function showToast(type, message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = message;

    toast.addEventListener('click', () => dismissToast(toast));
    container.appendChild(toast);

    setTimeout(() => dismissToast(toast), 5000);
}

function dismissToast(toast) {
    toast.style.animation = 'toast-out 0.3s ease-in forwards';
    setTimeout(() => toast.remove(), 300);
}

// ---------------------------------------------------------------
// Utility: Escape HTML
// ---------------------------------------------------------------
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
