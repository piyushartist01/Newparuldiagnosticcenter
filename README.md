# New Parul Diagnostic Center

A modern, premium medical diagnostic center website with Google Sheets integration for appointment bookings.

## Features

- **Modern UI**: CarePlus-inspired medical landing page design
- **Fully Responsive**: Works beautifully on desktop, tablet, and mobile
- **Smooth Animations**: Scroll-triggered fade-in effects, counter animations, and hover micro-interactions
- **Google Sheets Integration**: Appointment form data goes directly to a Google Sheet (like Google Forms)
- **Zero Backend**: Pure static frontend — host anywhere for free
- **SEO Optimized**: Proper meta tags, semantic HTML5, and accessibility

## Sections

1. **Hero** — Engaging headline with stats counter and medical team image
2. **About** — Company mission with feature highlights
3. **Services** — 6 service cards with pricing and book-now CTAs
4. **Process** — 4-step visual guide (Book → Collect → Process → Report)
5. **Booking Form** — Patient details form with validation and Google Sheets submission
6. **CTA** — Call-to-action banner
7. **Footer** — Contact info, links, and social media

## Quick Start

### Run Locally
```bash
cd backend
python app.py
```
Then open http://localhost:5000 in your browser.

### Set Up Google Sheets
See [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) for step-by-step instructions.

## Tech Stack

- **HTML5** + **CSS3** + **Vanilla JavaScript**
- **Google Fonts**: Outfit + Plus Jakarta Sans
- **Google Apps Script**: For serverless form submission to Google Sheets
- **Python**: Simple static file server for local development (standard library only)

## Deployment

This is a static website — deploy the `frontend/` folder to any static hosting:

- **GitHub Pages**: Push to a repo and enable Pages for the `frontend` directory
- **Netlify**: Drag and drop the `frontend` folder
- **Vercel**: Point to the `frontend` directory

## License

© 2025 New Parul Diagnostic Center. All rights reserved.
