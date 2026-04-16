/**
 * main.js — New Parul Diagnostic Center
 * Handles: Scroll animations, Navbar, Mobile menu, Counter animation,
 *          Form validation & Google Sheets submission, Toast notifications
 */

// ============================================================
// CONFIGURATION
// ============================================================
// Replace this URL with your Google Apps Script Web App URL after deploying the script
const GOOGLE_SHEETS_URL = '';

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
// SERVICE SELECTION (from service cards)
// ============================================================
window.selectService = function(serviceName) {
    const select = document.getElementById('serviceType');
    if (select) {
        select.value = serviceName;
        // Scroll to booking section (smooth scroll handled by CSS)
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
