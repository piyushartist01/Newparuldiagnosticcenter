import os
import re

html_path = 'c:/Users/oment/.gemini/antigravity/scratch/new-parul-diagnostic/frontend/index.html'
css_path = 'c:/Users/oment/.gemini/antigravity/scratch/new-parul-diagnostic/frontend/css/styles.css'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Remove .top-bar completely
html = re.sub(r'<!-- ============================================\s*TOP BAR.*?</div>\s*</div>', '', html, flags=re.DOTALL)

# Update Navigation Structure
nav_replacement = """
    <!-- ============================================
         HEADER (Single Green Navbar)
         ============================================ -->
    <nav class="navbar green-nav" role="navigation" aria-label="Main navigation">
        <div class="nav-container nav-container-flex" style="display:flex; justify-content:space-between; align-items:center; width:100%; height:70px;">
            <!-- Booking Button on Left -->
            <div class="nav-left">
                <a href="#appointment" class="btn btn-primary" style="background:white; color:var(--accent); font-weight:bold; box-shadow:none;">Book Test</a>
            </div>
            
            <!-- Logo on Right -->
            <div class="nav-right" style="display:flex; align-items:center; gap:10px;">
                <span class="brand-text" style="color:white; font-size:1.3rem; font-weight:bold;">New Parul Diagnostic</span>
                <img src="images/logo-placeholder.png" alt="Logo" class="logo-img" style="height:48px; background:white; padding:4px; border-radius:8px;" onerror="this.style.display='none'">
            </div>
        </div>
    </nav>
"""
html = re.sub(r'<!-- ============================================\s*NAVIGATION.*?</nav>', nav_replacement, html, flags=re.DOTALL)

# Update Hero Section
hero_replacement = """
    <!-- ============================================
         HERO SECTION (BANNER IMAGE)
         ============================================ -->
    <section class="hero full-banner" id="home">
        <div class="hero-image-wrapper">
            <img src="images/hero_banner.png" alt="Family Healthcare Banner" class="hero-banner-image">
            <div class="hero-banner-overlay">
                <div class="hero-badge" style="background:rgba(255,255,255,0.9); color:var(--accent); border:none;">🔬 Trusted Diagnostics Since 2010</div>
                <h1 style="color:white; font-size: clamp(2.5rem, 5vw, 3.5rem); line-height:1.2; margin-bottom:1rem; text-shadow: 2px 2px 8px rgba(0,0,0,0.6);">Comprehensive Health Packages For Your Family</h1>
                <p style="color:#f1f5f9; font-size: 1.15rem; max-width: 500px; text-shadow: 1px 1px 4px rgba(0,0,0,0.6);">Experience accurate, reliable, and affordable diagnostic services right at your doorstep.</p>
                <div class="hero-buttons" style="margin-top:2rem;">
                    <a href="#appointment" class="btn btn-primary btn-lg" style="font-size:1.1rem; padding:1rem 2.5rem; background:#10b981; border:none; color:white;">Book Now — Upto 60% OFF</a>
                </div>
            </div>
        </div>
    </section>
"""
html = re.sub(r'<!-- ============================================\s*HERO SECTION.*?</section>', hero_replacement, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Add styles for new navigation and banner
new_css = """
/* ---------------------------------------------------------------
   Updated Navbar & Hero Banner (Iteration 2)
   --------------------------------------------------------------- */
.green-nav {
    background: var(--accent) !important;
    padding: 0;
    backdrop-filter: none;
    border: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.full-banner {
    padding: 0 !important;
    min-height: auto;
    background: none;
    display: block;
}
.hero-image-wrapper {
    position: relative;
    width: 100%;
    height: 550px;
    overflow: hidden;
    background: #000;
}
.hero-banner-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 30%;
    opacity: 0.65;
    display: block;
}
.hero-banner-overlay {
    position: absolute;
    top: 50%;
    left: 5%;
    transform: translateY(-50%);
    max-width: 650px;
    z-index: 2;
    text-align: left;
}
@media (max-width: 768px) {
    .nav-container-flex { padding: 0 1rem; }
    .nav-left .btn { padding: 0.4rem 0.8rem; font-size: 0.8rem; }
    .nav-right .brand-text { font-size: 1rem !important; }
    .logo-img { height: 35px !important; }
    .hero-image-wrapper { height: 450px; }
    .hero-banner-overlay { left: 5%; right: 5%; text-align: center; margin: 0 auto; max-width: 100%; }
    .hero-banner-overlay h1 { font-size: 2rem !important; }
    .hero-buttons { justify-content: center !important; }
}
"""
with open(css_path, 'a', encoding='utf-8') as f:
    f.write(new_css)

print("HTML/CSS updated for Single Navbar and Hero Banner.")
