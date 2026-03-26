import re
import os

css_path = os.path.join(os.path.dirname(__file__), "css", "styles.css")
with open(css_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace variables
content = re.sub(r'--bg-hero:.*?;', '--bg-hero: #f0fdf4;', content)
content = re.sub(r'--accent:.*?;', '--accent: #006B3F;', content)
content = re.sub(r'--accent-light:.*?;', '--accent-light: #E8F5E9;', content)
content = re.sub(r'--accent-hover:.*?;', '--accent-hover: #00874e;', content)
content = re.sub(r'--accent-glow:.*?;', '--accent-glow: rgba(0, 107, 63, 0.15);', content)
content = re.sub(r'--shadow-glow:.*?;', '--shadow-glow: 0 0 30px rgba(0, 107, 63, 0.1);', content)

# 2. Update navbar position
content = re.sub(r'\.navbar\s*\{[^}]*\}', 
    '.navbar {\n    position: sticky;\n    top: 0;\n    z-index: 1000;\n    background: var(--nav-bg);\n    backdrop-filter: blur(20px);\n    border-bottom: 1px solid var(--border);\n    transition: all var(--transition);\n}', content)

# 3. Append new styles for Top Bar, Hero Layout, Timeline, Testimonials
new_css = """
/* ---------------------------------------------------------------
   Redesign Additions
   --------------------------------------------------------------- */
.top-bar {
    background: var(--accent);
    color: #fff;
    padding: 0.6rem 0;
    font-size: 0.85rem;
    z-index: 1001;
    position: relative;
}
.top-bar-inner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: auto;
}
.top-contact { display: flex; gap: 1.5rem; }
.top-bar .btn-primary {
    background: #fff;
    color: var(--accent);
    padding: 0.4rem 1.2rem;
    font-size: 0.85rem;
    border-radius: 8px;
    box-shadow: none;
}
.top-bar .btn-primary:hover {
    background: var(--bg-secondary);
    color: var(--accent);
    transform: translateY(-1px);
}

.logo-img { max-height: 48px; border-radius: 4px; }
.brand-text { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); }

.hero-container {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
    position: relative;
    z-index: 1;
}

.hero-content { text-align: left; }
.hero-content p { margin: 0 0 2.5rem; }
.hero-buttons { justify-content: flex-start; }
.hero h1 .gradient-text { background: none; -webkit-text-fill-color: initial; color: var(--accent); }
.hero { min-height: 80vh; padding: 4rem 2rem; background: var(--bg-hero); align-items: stretch; justify-content: flex-start; }
.hero::before, .hero::after { display: none; } /* remove floating circles */

.hero-form-card {
    background: var(--bg-card);
    padding: 2.5rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
}
.hero-form-card h3 { margin-bottom: 1.5rem; font-size: 1.25rem; }

.accreditation-ribbon {
    background: #fff;
    border-bottom: 1px solid var(--border);
    padding: 1.5rem 0;
}
.ribbon-grid {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.ribbon-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary);
}
.ribbon-item .icon { font-size: 1.25rem; }

.service-card { text-align: left; }
.card-tag {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: var(--warning);
    color: #fff;
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-weight: 700;
    text-transform: uppercase;
}
.service-params { color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 1.5rem; height: 40px;}
.price-block { display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 1rem; }
.old-price { text-decoration: line-through; color: var(--text-muted); font-size: 1rem; }

.timeline-container {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
    gap: 1rem;
    align-items: center;
    max-width: 1000px;
    margin: 3rem auto 0;
}
.timeline-step { text-align: center; }
.step-icon {
    width: 64px;
    height: 64px;
    background: var(--accent-light);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    margin: 0 auto 1rem;
    color: var(--accent);
}
.timeline-step h5 { font-size: 1.05rem; margin-bottom: 0.5rem; }
.timeline-step p { font-size: 0.85rem; color: var(--text-secondary); }
.timeline-line {
    height: 3px;
    background: var(--border);
    flex-grow: 1;
    position: relative;
    top: -30px;
}

.testimonials-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}
.testimonial-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem;
    box-shadow: var(--shadow-sm);
}
.quote { font-style: italic; color: var(--text-secondary); margin-bottom: 1.5rem; line-height: 1.7; }
.author { display: flex; align-items: center; gap: 1rem; }
.author .avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--accent-light);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.25rem;
}
.author h5 { font-size: 1rem; margin-bottom: 0.2rem; }
.author span { font-size: 0.8rem; color: var(--text-muted); }

.footer { background: var(--accent); color: #fff; }
.footer-brand p, .footer-col ul a, .footer-social a, .footer-col h4, .footer-bottom { color: #e2e8f0; }
.footer-social a { border-color: rgba(255,255,255,0.2); }
.footer-social a:hover { background: #fff; color: var(--accent); }
.footer-col ul a:hover { color: #fff; text-decoration: underline; }
.footer-bottom { border-top-color: rgba(255,255,255,0.1); }

@media (max-width: 768px) {
    .top-contact { display: none; }
    .hero-container { grid-template-columns: 1fr; }
    .hero-content { text-align: center; }
    .hero-buttons { justify-content: center; }
    .timeline-container {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    .timeline-line { display: none; }
    .timeline-step { display: flex; align-items: center; text-align: left; gap: 1.5rem; }
    .step-icon { margin: 0; flex-shrink: 0; }
}
"""

with open(css_path, "w", encoding="utf-8") as f:
    f.write(content + "\n" + new_css)

print("CSS updated successfully!")
