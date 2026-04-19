/**
 * main.js — New Parul Diagnostic Center
 * Handles: Scroll animations, Navbar, Mobile menu, Counter animation,
 *          Form validation & Google Sheets submission, Toast notifications,
 *          Dynamic services loading from Google Sheets
 */

// ============================================================
// CONFIGURATION
// ============================================================
// Google Apps Script Web App URL (handles both appointments POST and services GET)
const GOOGLE_SHEETS_URL = 'https://script.google.com/macros/s/AKfycbyprmVNK-Rvutrq457qs2ef0CJKMCKY-Yt6UEaKG6Ga0wo0ddll7OepvH7GVcyvYWxZfA/exec';

// ============================================================
// FALLBACK SERVICES (used if Google Sheets fetch fails)
// ============================================================
const FALLBACK_SERVICES = [
    { name: 'Complete Blood Count (CBC)', description: 'Comprehensive blood test measuring red blood cells, white blood cells, hemoglobin, and platelets.', price: 350, originalPrice: 525, icon: '🩸', active: true },
    { name: 'Blood Sugar (Fasting / PP)', description: 'Measures blood glucose levels to screen for diabetes and monitor blood sugar control.', price: 150, originalPrice: 225, icon: '💉', active: true },
    { name: 'Lipid Profile', description: 'Measures cholesterol levels including HDL, LDL, triglycerides, and total cholesterol.', price: 500, originalPrice: 750, icon: '❤️', active: true },
    { name: 'Thyroid Profile (T3, T4, TSH)', description: 'Evaluates thyroid gland function by measuring T3, T4, and TSH hormone levels.', price: 600, originalPrice: 900, icon: '🦋', active: true },
    { name: 'ECG (Electrocardiogram)', description: 'Records the electrical activity of the heart to detect cardiac conditions and irregularities.', price: 300, originalPrice: 450, icon: '🫀', active: true },
    { name: 'Ultrasound', description: 'Non-invasive imaging using sound waves to examine internal organs and tissues safely.', price: 800, originalPrice: 1200, icon: '🔬', active: true },
];

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    initScrollProgress();
    initNavbar();
    initMobileMenu();
    initCounterAnimation();
    initFormDateMin();
    loadServicesFromSheet(); // Dynamic services from Google Sheets

    const form = document.getElementById('appointmentForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    initFormClearErrors();
});

// ============================================================
// SCROLL ANIMATIONS (Intersection Observer)
// ============================================================
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        root: null,
        rootMargin: '0px 0px -60px 0px',
        threshold: 0.1
    });

    document.querySelectorAll('.fade-up, .fade-left, .fade-right').forEach(el => {
        observer.observe(el);
    });
}

// ============================================================
// SCROLL PROGRESS BAR
// ============================================================
function initScrollProgress() {
    const progressBar = document.getElementById('scrollProgress');
    if (!progressBar) return;

    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
    }, { passive: true });
}

// ============================================================
// NAVBAR — Sticky with blur effect + active link highlighting
// ============================================================
function initNavbar() {
    const nav = document.getElementById('navbar');
    const navLinks = document.querySelectorAll('.nav-links a');
    const sections = document.querySelectorAll('section[id]');

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }

        // Active link highlighting
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            if (window.scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }, { passive: true });
}

// ============================================================
// MOBILE MENU
// ============================================================
function initMobileMenu() {
    const btn = document.getElementById('mobileMenuBtn');
    const overlay = document.getElementById('mobileMenu');
    const links = document.querySelectorAll('.mobile-link');

    if (!btn || !overlay) return;

    btn.addEventListener('click', () => {
        btn.classList.toggle('active');
        overlay.classList.toggle('active');
        document.body.style.overflow = overlay.classList.contains('active') ? 'hidden' : '';
    });

    links.forEach(link => {
        link.addEventListener('click', () => {
            btn.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
}

// ============================================================
// COUNTER ANIMATION (Stats in Hero)
// ============================================================
function initCounterAnimation() {
    const counters = document.querySelectorAll('[data-count]');
    if (counters.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-count'));
                animateCounter(el, target);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element, target) {
    const duration = 2000;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out cubic
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(easedProgress * target);

        if (target >= 10000) {
            element.textContent = (current / 1000).toFixed(current >= target ? 0 : 1) + 'k+';
        } else if (target >= 100) {
            element.textContent = current + '+';
        } else {
            element.textContent = current + (target === 24 ? 'h' : '+');
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// ============================================================
// FORM — Set minimum date to today
// ============================================================
function initFormDateMin() {
    const dateInput = document.getElementById('appointmentDate');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }
}

// ============================================================
// FORM — Clear errors on input (real-time feedback)
// ============================================================
function initFormClearErrors() {
    const fieldErrorMap = {
        'patientName': 'patientNameError',
        'patientPhone': 'patientPhoneError',
        'patientEmail': 'patientEmailError',
        'appointmentDate': 'appointmentDateError',
        'serviceType': 'serviceTypeError'
    };

    Object.entries(fieldErrorMap).forEach(([fieldId, errorId]) => {
        const field = document.getElementById(fieldId);
        const error = document.getElementById(errorId);
        if (field && error) {
            field.addEventListener('input', () => error.classList.remove('visible'));
            field.addEventListener('change', () => error.classList.remove('visible'));
        }
    });
}

// ============================================================
// DYNAMIC SERVICES — Google Sheets Integration
// ============================================================

/**
 * Fetches services from the Google Sheet via Apps Script doGet.
 * Falls back to FALLBACK_SERVICES if the request fails.
 */
async function loadServicesFromSheet() {
    showServiceSkeletons();

    let services = FALLBACK_SERVICES;

    if (GOOGLE_SHEETS_URL) {
        try {
            const url = `${GOOGLE_SHEETS_URL}?action=services`;
            const res = await fetch(url, { method: 'GET', mode: 'cors' });
            if (res.ok) {
                const data = await res.json();
                if (data.result === 'success' && Array.isArray(data.services) && data.services.length > 0) {
                    services = data.services.filter(s => String(s.active).toUpperCase() === 'TRUE');
                }
            }
        } catch (err) {
            console.warn('Services fetch failed, using fallback data.', err);
        }
    }

    renderServiceCards(services);
    renderBookingDropdown(services);
    // Re-init scroll animations for dynamically added cards
    initScrollAnimations();
}

/** Shows placeholder skeleton cards while loading */
function showServiceSkeletons() {
    const grid = document.getElementById('servicesGrid');
    if (!grid) return;
    grid.innerHTML = Array(6).fill(0).map(() => `
        <div class="service-card skeleton-card">
            <div class="skeleton skeleton-icon"></div>
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-desc"></div>
            <div class="skeleton skeleton-desc short"></div>
            <div class="skeleton skeleton-btn"></div>
        </div>
    `).join('');
}

/** Renders service cards dynamically from sheet data */
function renderServiceCards(services) {
    const grid = document.getElementById('servicesGrid');
    if (!grid) return;

    const delays = ['', 'delay-1', 'delay-2', 'delay-3', 'delay-4', 'delay-5'];

    if (services.length === 0) {
        grid.innerHTML = '<p style="text-align:center;color:var(--text-muted);grid-column:1/-1;">No services available right now. Please call us directly.</p>';
        return;
    }

    grid.innerHTML = services.map((s, i) => `
        <div class="service-card fade-up ${delays[i % delays.length]}">
            <div class="service-icon">${s.icon || '🔬'}</div>
            <h4>${s.name}</h4>
            <p class="service-desc">${s.description}</p>
            <div class="service-price-row">
                <div>
                    <span class="service-price">₹${Number(s.price).toLocaleString('en-IN')}</span>
                    ${s.originalPrice ? `<span class="service-price-old">₹${Number(s.originalPrice).toLocaleString('en-IN')}</span>` : ''}
                </div>
                <a href="#book-test" class="service-book-btn" onclick="selectService('${s.name}')">Book Now →</a>
            </div>
        </div>
    `).join('');
}

/** Populates the booking form dropdown from sheet data */
function renderBookingDropdown(services) {
    const select = document.getElementById('serviceType');
    if (!select) return;

    // Keep the default empty option, then rebuild the rest
    select.innerHTML = '<option value="">Choose a test package...</option>' +
        services.map(s =>
            `<option value="${s.name}">${s.name} — ₹${Number(s.price).toLocaleString('en-IN')}</option>`
        ).join('');
}

// ============================================================
// SERVICE SELECTION (from service cards)
// ============================================================
window.selectService = function(serviceName) {
    const select = document.getElementById('serviceType');
    if (select) {
        select.value = serviceName;
    }
};


// ============================================================
// FORM SUBMISSION — Google Sheets Integration
// ============================================================
async function handleFormSubmit(e) {
    e.preventDefault();

    // Clear previous errors
    document.querySelectorAll('.error-msg').forEach(el => el.classList.remove('visible'));

    // Get values
    const name = document.getElementById('patientName').value.trim();
    const phone = document.getElementById('patientPhone').value.trim();
    const email = document.getElementById('patientEmail').value.trim();
    const date = document.getElementById('appointmentDate').value;
    const time = document.getElementById('appointmentTime').value;
    const service = document.getElementById('serviceType').value;

    // Validate
    let hasError = false;

    if (!name || name.length < 2) {
        showError('patientNameError');
        hasError = true;
    }

    if (!phone || !/^[\d\s\+\-\(\)]{7,20}$/.test(phone)) {
        showError('patientPhoneError');
        hasError = true;
    }

    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showError('patientEmailError');
        hasError = true;
    }

    if (!date) {
        showError('appointmentDateError');
        hasError = true;
    } else {
        const selectedDate = new Date(date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (selectedDate < today) {
            showError('appointmentDateError');
            hasError = true;
        }
    }

    if (!service) {
        showError('serviceTypeError');
        hasError = true;
    }

    if (hasError) return;

    // Submit
    const submitBtn = document.getElementById('submitBtn');
    const originalHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = 'Submitting... <span class="spinner"></span>';
    submitBtn.disabled = true;

    const formData = {
        timestamp: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
        name: name,
        phone: phone,
        email: email || 'Not provided',
        date: date,
        time: time || 'Not specified',
        service: service
    };

    try {
        if (GOOGLE_SHEETS_URL) {
            // Send to Google Sheets
            await fetch(GOOGLE_SHEETS_URL, {
                method: 'POST',
                mode: 'no-cors',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        }

        // Always show success (no-cors doesn't return readable response)
        showToast('🎉 Appointment booked successfully! We will contact you soon.', 'success');
        e.target.reset();
        initFormDateMin(); // Reset date min

    } catch (err) {
        console.error('Submission error:', err);
        showToast('❌ Something went wrong. Please call us directly at +91 98765 43210.', 'error');
    } finally {
        submitBtn.innerHTML = originalHTML;
        submitBtn.disabled = false;
    }
}

function showError(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('visible');
}

// ============================================================
// TOAST NOTIFICATIONS
// ============================================================
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 5000);
}
