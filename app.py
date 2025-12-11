"""
Mediaforce Proposal Generator - Web Application
Flask-based web interface for staff to create proposals
"""

import os
import json
import secrets
import re
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from authlib.integrations.flask_client import OAuth

# Anthropic API for AI generation
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    Anthropic = None

# Import proposal generation modules (optional - for AI generation)
try:
    from generator import ProposalGenerator
    from assembler import ProposalAssembler
    HAS_GENERATOR = True
except ImportError:
    HAS_GENERATOR = False
    ProposalGenerator = None
    ProposalAssembler = None

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# OAuth Setup
oauth = OAuth(app)

# Google OAuth configuration
if os.environ.get('GOOGLE_CLIENT_ID'):
    google = oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'email profile'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    )
else:
    google = None

# Allowed email domains for staff access
ALLOWED_DOMAINS = os.environ.get('ALLOWED_DOMAINS', 'mediaforce.ca').split(',')


def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth in development mode
        if os.environ.get('FLASK_ENV') == 'development' and os.environ.get('SKIP_AUTH'):
            return f(*args, **kwargs)

        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def is_allowed_user(email):
    """Check if user email is from allowed domain"""
    if not email:
        return False
    domain = email.split('@')[-1]
    return domain in ALLOWED_DOMAINS


@app.route('/')
def index():
    """Landing page"""
    # Auto-login if SKIP_AUTH is enabled
    if os.environ.get('SKIP_AUTH', '').lower() == 'true':
        if 'user' not in session:
            session['user'] = {
                'email': 'staff@mediaforce.ca',
                'name': 'Mediaforce Staff'
            }
        return redirect(url_for('dashboard'))

    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('web/index.html')


@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    if not google:
        # Development mode - auto-login
        if os.environ.get('FLASK_ENV') == 'development':
            session['user'] = {
                'email': 'dev@mediaforce.ca',
                'name': 'Development User'
            }
            return redirect(url_for('dashboard'))
        return "OAuth not configured", 500

    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    """Handle OAuth callback"""
    if not google:
        return redirect(url_for('dashboard'))

    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()

    if not is_allowed_user(user_info.get('email')):
        flash('Access denied. Only Mediaforce staff can use this application.', 'error')
        return redirect(url_for('index'))

    session['user'] = {
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture')
    }

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    """Log out user"""
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for creating proposals"""
    return render_template('web/dashboard.html', user=session.get('user'))


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_proposal():
    """Create a new proposal"""
    if request.method == 'GET':
        return render_template('web/create.html', user=session.get('user'))

    # Handle form submission
    try:
        metadata = build_metadata_from_form(request.form)
        return render_template('web/preview.html',
                             metadata=metadata,
                             user=session.get('user'))
    except Exception as e:
        flash(f'Error processing form: {str(e)}', 'error')
        return redirect(url_for('create_proposal'))


@app.route('/api/generate', methods=['POST'])
@login_required
def api_generate():
    """API endpoint to generate proposal HTML"""
    try:
        metadata = request.json

        if HAS_GENERATOR and ProposalAssembler:
            assembler = ProposalAssembler()
            html_content = assembler.generate(metadata)
        else:
            html_content = generate_simple_preview(metadata)

        return jsonify({
            'success': True,
            'html': html_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/preview', methods=['POST'])
@login_required
def api_preview():
    """Generate a preview of the proposal"""
    try:
        metadata = request.json
        preview_html = generate_simple_preview(metadata)

        return jsonify({
            'success': True,
            'html': preview_html
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-from-text', methods=['POST'])
@login_required
def api_generate_from_text():
    """Generate proposal from pasted text"""
    try:
        text = request.json.get('text', '')
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400

        # Parse the text and generate proposal
        html = generate_proposal_from_text(text)

        return jsonify({
            'success': True,
            'html': html
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def parse_client_text(text):
    """Parse free-form text to extract client information"""
    import re

    data = {
        'company': '',
        'industry': '',
        'location': '',
        'challenges': [],
        'goals': [],
        'budget': '',
        'services': [],
        'contact': '',
        'website': '',
        'audience': '',
        'competitors': []
    }

    lines = text.strip().split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        lower = line.lower()

        # Detect section headers
        if any(x in lower for x in ['company:', 'business:', 'client:', 'name:']):
            data['company'] = re.sub(r'^[^:]+:\s*', '', line)
            current_section = None
        elif any(x in lower for x in ['industry:', 'sector:']):
            data['industry'] = re.sub(r'^[^:]+:\s*', '', line)
            current_section = None
        elif any(x in lower for x in ['location:', 'city:', 'address:']):
            data['location'] = re.sub(r'^[^:]+:\s*', '', line)
            current_section = None
        elif any(x in lower for x in ['budget:', 'investment:', 'spend:']):
            data['budget'] = re.sub(r'^[^:]+:\s*', '', line)
            current_section = None
        elif any(x in lower for x in ['website:', 'url:', 'site:']):
            data['website'] = re.sub(r'^[^:]+:\s*', '', line)
            current_section = None
        elif any(x in lower for x in ['contact:', 'email:', 'phone:']):
            data['contact'] = re.sub(r'^[^:]+:\s*', '', line)
            current_section = None
        elif any(x in lower for x in ['audience:', 'target:', 'customer']):
            if ':' in line:
                data['audience'] = re.sub(r'^[^:]+:\s*', '', line)
            current_section = 'audience'
        elif any(x in lower for x in ['challenge', 'problem', 'pain', 'issue', 'struggle']):
            current_section = 'challenges'
        elif any(x in lower for x in ['goal', 'objective', 'target', 'want', 'aim']):
            current_section = 'goals'
        elif any(x in lower for x in ['service', 'need', 'looking for', 'interest']):
            if ':' in line:
                services_text = re.sub(r'^[^:]+:\s*', '', line)
                data['services'] = [s.strip() for s in re.split(r'[,;]', services_text) if s.strip()]
            current_section = 'services'
        elif any(x in lower for x in ['competitor', 'competition']):
            current_section = 'competitors'
        elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
            # Bullet point - add to current section
            item = line.lstrip('-•* ').strip()
            if current_section == 'challenges':
                data['challenges'].append(item)
            elif current_section == 'goals':
                data['goals'].append(item)
            elif current_section == 'services':
                data['services'].append(item)
            elif current_section == 'competitors':
                data['competitors'].append(item)
        elif current_section and line:
            # Non-bullet continuation
            if current_section == 'challenges':
                data['challenges'].append(line)
            elif current_section == 'goals':
                data['goals'].append(line)

    # Extract budget number if present
    if data['budget']:
        budget_match = re.search(r'\$?([\d,]+)', data['budget'])
        if budget_match:
            data['budget_num'] = int(budget_match.group(1).replace(',', ''))
        else:
            data['budget_num'] = 2500
    else:
        data['budget_num'] = 2500

    # Default services if none found
    if not data['services']:
        data['services'] = ['Google Ads', 'SEO']

    return data


def build_proposal_with_ai_content(company, industry, location, budget, management_fee, ad_spend, today, ai_content, services):
    """Build the full proposal HTML with AI-generated content matching local template design"""

    # Determine service badges and build service price items
    has_google_ads = any('google' in s.lower() or 'ads' in s.lower() or 'ppc' in s.lower() for s in services)
    has_seo = any('seo' in s.lower() for s in services)
    has_social = any('social' in s.lower() or 'facebook' in s.lower() or 'instagram' in s.lower() or 'linkedin' in s.lower() for s in services)
    has_website = any('web' in s.lower() or 'site' in s.lower() for s in services)

    # Build service-specific pricing items
    price_items_html = ''
    total_monthly = 0

    if has_google_ads:
        price_items_html += f'''
                        <div class="price-item">
                            <span class="label">Google Ads Management</span>
                            <span class="amount">${management_fee:,}/month</span>
                        </div>'''
        total_monthly += management_fee

    if has_seo:
        seo_fee = 1100 if budget > 2000 else 799
        price_items_html += f'''
                        <div class="price-item">
                            <span class="label">SEO Management</span>
                            <span class="amount">${seo_fee:,}/month</span>
                        </div>'''
        total_monthly += seo_fee

    if has_social:
        social_fee = 800 if budget > 2000 else 599
        price_items_html += f'''
                        <div class="price-item">
                            <span class="label">Social Media / LinkedIn Marketing</span>
                            <span class="amount">${social_fee:,}/month</span>
                        </div>'''
        total_monthly += social_fee

    if has_website:
        price_items_html += '''
                        <div class="price-item">
                            <span class="label">Website Design & Development</span>
                            <span class="amount">$5,000 - $15,000</span>
                        </div>'''

    # Add ad spend
    price_items_html += f'''
                        <div class="price-item">
                            <span class="label">Recommended Ad Spend</span>
                            <span class="amount">${ad_spend:,}/month</span>
                        </div>'''

    # Total line
    total_monthly += ad_spend
    price_items_html += f'''
                        <div class="price-item" style="border-top: 2px solid rgba(255,204,51,0.5); padding-top: 15px; margin-top: 15px; background: rgba(255,204,51,0.15); border-radius: 8px; padding: 15px;">
                            <span class="label" style="font-size: 14pt;">Total Monthly Investment</span>
                            <span class="amount" style="font-size: 18pt;">${total_monthly:,}/month</span>
                        </div>'''

    # Navigation menu items
    nav_items = '''
                    <li class="nav-menu-item"><a href="#executive-summary" class="nav-menu-link">Executive Summary</a></li>
                    <li class="nav-menu-item"><a href="#your-business" class="nav-menu-link">Your Business</a></li>
                    <li class="nav-menu-item"><a href="#goals" class="nav-menu-link">Goals</a></li>
                    <li class="nav-menu-item"><a href="#strategy" class="nav-menu-link">Strategy</a></li>
                    <li class="nav-menu-item"><a href="#timeline" class="nav-menu-link">Timeline</a></li>
                    <li class="nav-menu-item"><a href="#investment" class="nav-menu-link">Investment</a></li>
                    <li class="nav-menu-item"><a href="#about-mediaforce" class="nav-menu-link">About Us</a></li>
                    <li class="nav-menu-item"><a href="#next-steps" class="nav-menu-link">Next Steps</a></li>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company} - Digital Marketing Proposal - Mediaforce</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 10pt;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            -webkit-font-smoothing: antialiased;
        }}
        html {{ scroll-behavior: smooth; }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            position: relative;
        }}

        /* Header */
        .header {{
            background: white;
            color: #333;
            padding: 25px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #0e5881;
        }}
        .logo-container {{ flex: 1; }}
        .header-info {{ text-align: right; }}
        .header-info h1 {{ font-size: 18pt; margin-bottom: 5px; color: #0e5881; }}
        .header-info p {{ font-size: 9pt; color: #666; }}

        /* Sticky Navigation Menu */
        .nav-menu {{
            position: -webkit-sticky;
            position: sticky;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%);
            z-index: 9999;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            border-bottom: 3px solid #ffcc33;
        }}
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            padding: 0 20px;
            overflow-x: auto;
            scrollbar-width: none;
        }}
        .nav-container::-webkit-scrollbar {{ display: none; }}
        .nav-menu-items {{
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            gap: 5px;
            flex-wrap: nowrap;
            white-space: nowrap;
        }}
        .nav-menu-item {{ position: relative; }}
        .nav-menu-link {{
            display: block;
            padding: 18px 20px;
            color: white;
            text-decoration: none;
            font-size: 10pt;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            border-bottom: 3px solid transparent;
        }}
        .nav-menu-link:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: #ffcc33;
            border-bottom-color: #ffcc33;
        }}
        .nav-menu-link.active {{
            background: rgba(255, 255, 255, 0.15);
            color: #ffcc33;
            border-bottom-color: #ffcc33;
        }}
        .nav-menu-toggle {{
            display: none;
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.4);
            border-radius: 8px;
            color: white;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            padding: 10px 15px;
            margin-left: auto;
            transition: all 0.3s ease;
            line-height: 1;
            min-width: 50px;
            min-height: 50px;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}
        .nav-menu-toggle:hover {{
            background: rgba(255, 255, 255, 0.25);
            border-color: rgba(255, 255, 255, 0.6);
            transform: scale(1.05);
        }}

        /* Cover Section */
        .cover {{
            background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        .cover h1 {{
            font-size: 32pt;
            margin-bottom: 15px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .cover h2 {{
            font-size: 18pt;
            font-weight: 400;
            margin-bottom: 20px;
            color: white;
            opacity: 0.95;
        }}
        .cover .meta {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            background: rgba(255,255,255,0.15);
            padding: 15px 25px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            min-width: 180px;
        }}
        .meta-item strong {{
            display: block;
            font-size: 9pt;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 5px;
            opacity: 0.9;
        }}
        .meta-item span {{ font-size: 16pt; font-weight: 700; }}

        /* Content Sections */
        .content {{ padding: 30px 40px; }}
        .section {{ margin-bottom: 30px; page-break-inside: avoid; }}
        h2 {{
            color: #0e5881;
            font-size: 18pt;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 3px solid #ffcc33;
            page-break-after: avoid;
        }}
        h3 {{ color: #2d2d2d; font-size: 14pt; margin: 20px 0 10px 0; page-break-after: avoid; }}
        h4 {{ color: #444; font-size: 12pt; margin: 15px 0 8px 0; page-break-after: avoid; }}
        p {{ color: #555; margin-bottom: 10px; line-height: 1.7; }}
        ul, ol {{ margin: 10px 0 10px 30px; color: #555; }}
        li {{ margin-bottom: 6px; line-height: 1.6; color: inherit; }}

        /* Highlight Boxes */
        .info-box {{
            background: #e8f4f8;
            border-left: 4px solid #0e5881;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
            page-break-inside: avoid;
        }}
        .success-box {{
            background: #E8F5E9;
            border-left: 4px solid #4CAF50;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
            page-break-inside: avoid;
        }}
        .warning-box {{
            background: #FFF3E0;
            border-left: 4px solid #FF9800;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
            page-break-inside: avoid;
        }}

        /* Price Box */
        .price-box {{
            background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin: 25px 0;
            box-shadow: 0 10px 30px rgba(14,88,129,0.3);
            page-break-inside: avoid;
            border: 3px solid #ffcc33;
        }}
        .price-box h3 {{ color: white; margin-top: 0; font-size: 16pt; margin-bottom: 15px; }}
        .price-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .price-item .label {{ font-size: 12pt; font-weight: 500; color: white; }}
        .price-item .amount {{ font-size: 16pt; font-weight: 700; color: white; }}
        .price-box p, .price-box ul, .price-box ol, .price-box li, .price-box h4 {{ color: white; }}

        /* Cards */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .card {{
            background: #f9f9f9;
            border-left: 4px solid #ffcc33;
            padding: 20px;
            border-radius: 8px;
            transition: transform 0.3s, box-shadow 0.3s;
            page-break-inside: avoid;
        }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
        .card h4 {{ color: #0e5881; margin-top: 0; font-size: 13pt; }}

        /* Checklist */
        .checklist {{ list-style: none; padding-left: 0; }}
        .checklist li {{ padding-left: 30px; position: relative; margin-bottom: 8px; }}
        .checklist li:before {{
            content: "\\2713";
            position: absolute;
            left: 0;
            color: #4CAF50;
            font-weight: bold;
            font-size: 14pt;
        }}

        /* Footer */
        .footer {{
            background: #1a1a1a;
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        .footer p {{ color: #ccc; margin: 5px 0; font-size: 9pt; }}
        .footer strong {{ color: #ffcc33; }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .nav-menu {{
                position: -webkit-sticky !important;
                position: sticky !important;
                top: 0 !important;
                z-index: 9999 !important;
            }}
            .nav-container {{
                flex-wrap: wrap;
                position: relative;
                min-height: 65px;
                padding: 10px 20px;
            }}
            .nav-menu-items {{
                flex-direction: column;
                width: 100%;
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.4s ease-in-out;
            }}
            .nav-menu-items.active {{
                max-height: 800px;
                padding-bottom: 10px;
            }}
            .nav-menu-toggle {{
                display: flex !important;
                position: fixed;
                right: 15px;
                top: 10px;
                z-index: 10001 !important;
                width: 55px;
                height: 55px;
                background: rgba(255, 204, 51, 0.3);
                border: 3px solid #ffcc33;
            }}
            .nav-menu-link {{
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                border-left: 3px solid transparent;
                padding: 15px 20px;
            }}
            .header {{ flex-direction: column; text-align: center; }}
            .header-info {{ text-align: center; margin-top: 15px; }}
            .content {{ padding: 20px; }}
            .cover h1 {{ font-size: 24pt; }}
            .card-grid {{ grid-template-columns: 1fr !important; }}
            body {{ font-size: 11pt; }}
            .meta {{ flex-direction: column; gap: 15px !important; }}
            .meta-item {{ min-width: auto; width: 100%; }}
        }}

        /* Print Styles */
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
            .nav-menu {{ display: none; }}
            .section, .card, .info-box, .success-box, .warning-box, .price-box {{ page-break-inside: avoid; }}
            h2, h3, h4 {{ page-break-after: avoid; }}
        }}
    </style>
    <script>
        window.addEventListener('DOMContentLoaded', () => {{
            const navToggle = document.getElementById('navToggle');
            const navMenu = document.getElementById('navMenu');

            if (navToggle) {{
                navToggle.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    navMenu.classList.toggle('active');
                }});
                document.addEventListener('click', (e) => {{
                    if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {{
                        navMenu.classList.remove('active');
                    }}
                }});
            }}

            document.querySelectorAll('.nav-menu-link').forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    const targetSection = document.querySelector(targetId);
                    if (targetSection) {{
                        const navHeight = document.querySelector('.nav-menu').offsetHeight;
                        const targetPosition = targetSection.offsetTop - navHeight;
                        window.scrollTo({{ top: targetPosition, behavior: 'smooth' }});
                        navMenu.classList.remove('active');
                    }}
                }});
            }});

            const sections = document.querySelectorAll('.section');
            const navLinks = document.querySelectorAll('.nav-menu-link');
            function highlightNavigation() {{
                let current = '';
                sections.forEach(section => {{
                    const sectionTop = section.offsetTop;
                    if (window.pageYOffset >= sectionTop - 200) {{
                        current = section.getAttribute('id');
                    }}
                }});
                navLinks.forEach(link => {{
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${{current}}`) {{
                        link.classList.add('active');
                    }}
                }});
            }}
            window.addEventListener('scroll', highlightNavigation);
            highlightNavigation();
        }});
    </script>
</head>
<body>
    <div class="container">
        <!-- Header with Logo -->
        <div class="header">
            <div class="logo-container">
                <img src="https://mediaforce.ca/wp-content/uploads/2025/10/mf-logo2.png" alt="Mediaforce" style="height: 60px; width: auto;">
            </div>
            <div class="header-info">
                <h1>Marketing Proposal</h1>
                <p>Prepared for {company}</p>
                <p>{today}</p>
            </div>
        </div>

        <!-- Navigation Menu -->
        <nav class="nav-menu">
            <div class="nav-container">
                <ul class="nav-menu-items" id="navMenu">
                    {nav_items}
                </ul>
                <button class="nav-menu-toggle" id="navToggle">&#9776;</button>
            </div>
        </nav>

        <!-- Cover Section -->
        <div class="cover">
            <h1>{company}</h1>
            <h2>Strategic Digital Marketing Proposal</h2>
            <p style="font-size: 12pt; margin-top: 20px; color: white;">Driving Lead Generation & Customer Acquisition</p>

            <div class="meta">
                <div class="meta-item">
                    <strong>Location</strong>
                    <span>{location if location else 'Canada'}</span>
                </div>
                <div class="meta-item">
                    <strong>Services</strong>
                    <span>{len(services)}-Channel Strategy</span>
                </div>
                <div class="meta-item">
                    <strong>Monthly Budget</strong>
                    <span>${budget:,}/mo</span>
                </div>
            </div>
        </div>

        <!-- Content -->
        <div class="content">

            <!-- Executive Summary -->
            <section id="executive-summary" class="section">
                <h2>&#128202; Executive Summary</h2>
                {extract_section(ai_content, 'EXECUTIVE SUMMARY', 'UNDERSTANDING YOUR BUSINESS')}
            </section>

            <!-- Understanding Your Business -->
            <section id="your-business" class="section">
                <h2>&#127970; Understanding Your Business</h2>
                {extract_section(ai_content, 'UNDERSTANDING YOUR BUSINESS', 'YOUR GOALS')}
            </section>

            <!-- Goals & Vision -->
            <section id="goals" class="section">
                <h2>&#127919; Your Goals & Vision for Success</h2>
                {extract_section(ai_content, 'YOUR GOALS', 'OUR STRATEGY')}
            </section>

            <!-- Strategy -->
            <section id="strategy" class="section">
                <h2>&#128640; Our Strategy & Approach</h2>
                {extract_section(ai_content, 'OUR STRATEGY', 'IMPLEMENTATION')}
            </section>

            <!-- Timeline -->
            <section id="timeline" class="section">
                <h2>&#128197; Implementation Timeline</h2>
                {extract_section(ai_content, 'IMPLEMENTATION', 'INVESTMENT')}
            </section>

            <!-- Investment -->
            <section id="investment" class="section">
                <h2>&#128176; Investment & Pricing</h2>

                <div class="price-box">
                    <h3>&#127919; Your Monthly Investment</h3>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        {price_items_html}
                    </div>
                </div>

                <div style="color: #333;">
                    {extract_section(ai_content, 'INVESTMENT', 'NEXT STEPS')}
                </div>
            </section>

            <!-- About Mediaforce -->
            <section id="about-mediaforce" class="section">
                <h2>&#127970; About Mediaforce</h2>

                <div class="success-box">
                    <h3 style="margin-top: 0;">Your Digital Growth Partner</h3>
                    <p>Mediaforce is a full-service digital marketing agency with deep expertise in website development, lead generation, and growth marketing for B2B professional services firms.</p>
                </div>

                <h3>Why Choose Mediaforce?</h3>
                <ul class="checklist">
                    <li><strong>Proven Track Record:</strong> Years of experience delivering results for Canadian businesses</li>
                    <li><strong>Data-Driven Approach:</strong> Every decision backed by analytics and performance data</li>
                    <li><strong>Full-Service Capability:</strong> From strategy to execution, all under one roof</li>
                    <li><strong>Dedicated Team:</strong> Direct access to senior strategists, not junior account managers</li>
                    <li><strong>Transparent Reporting:</strong> Clear, actionable insights delivered monthly</li>
                </ul>

                <!-- Client Referral - Augusto Bresolin -->
                <h3>Client Reference</h3>
                <div class="info-box">
                    <h4 style="margin-top: 0;">PNL Communications - Satisfied Client</h4>
                    <p>We've worked with PNL Communications on their digital marketing and website development. Feel free to reach out to learn about their experience working with Mediaforce.</p>

                    <div style="background: white; border-radius: 8px; border-left: 4px solid #0e5881; padding: 20px; margin-top: 20px;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <img src="https://mediaforce.ca/wp-content/uploads/2025/11/1751996871221.jpeg" alt="Augusto Bresolin" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                            <div>
                                <p style="margin: 0; font-weight: 600; color: #333;">Augusto Bresolin</p>
                                <p style="margin: 5px 0; color: #666; font-size: 10pt;">He/Him</p>
                                <p style="margin: 0; color: #666; font-size: 10pt;">Project Process Analyst, PNL Communications</p>
                            </div>
                        </div>
                        <p style="margin: 10px 0; color: #333;"><strong>&#128222;</strong> (902) 431-3131</p>
                        <p style="margin: 10px 0; color: #333;"><strong>&#128231;</strong> augusto@pnl.ca</p>
                        <p style="margin: 10px 0; color: #333;"><strong>&#127760;</strong> www.pnl.ca</p>
                    </div>
                </div>

                <!-- Contact Information - Joe Bongiorno -->
                <h3>Contact Information</h3>
                <div class="info-box" style="text-align: center;">
                    <p><strong>We're here to answer any questions about this proposal, our approach, or how we'll achieve your goals.</strong></p>
                    <div style="margin: 20px 0;">
                        <img src="https://mediaforce.ca/wp-content/uploads/2025/11/Joe-Bongiorno.png" alt="Joe Bongiorno" style="width: 120px; height: auto; border-radius: 50%; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    </div>
                    <p style="margin-top: 15px; color: #333;"><strong>Joe Bongiorno</strong><br>
                    Digital Marketing Strategist</p>
                    <p style="margin-top: 10px; color: #333;">&#128231; Email: <strong>jbon@mediaforce.ca</strong></p>
                    <p style="color: #333;">&#128222; Phone: <strong>613-265-2120</strong></p>
                    <p style="color: #333;">&#127760; Website: <strong>www.mediaforce.ca</strong></p>
                    <p style="margin-top: 15px; color: #333;"><strong>Response Time:</strong> Same business day</p>
                </div>
            </section>

            <!-- Next Steps -->
            <section id="next-steps" class="section">
                <h2>&#9989; Next Steps</h2>
                {extract_section(ai_content, 'NEXT STEPS', None)}

                <div class="success-box" style="margin-top: 30px;">
                    <h3 style="margin-top: 0;">Let's Build Your Lead Generation Engine</h3>
                    <p style="color: #333;">With the right digital marketing strategy, {company} can establish itself as a leader in your market. We're committed to delivering reliable, measurable results.</p>
                    <p style="margin-top: 15px; font-size: 12pt; color: #333;"><strong>Ready to get started? Let's schedule your kickoff call.</strong></p>
                </div>
            </section>

        </div>

        <!-- Footer Logos -->
        <div style="text-align: center; margin: 40px 0 20px 0;">
            <img src="https://mediaforce.ca/wp-content/uploads/2025/11/footer-logos.png" alt="Partner Platforms" style="max-width: 100%; height: auto;">
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>MEDIAFORCE</strong> - Digital Marketing Excellence</p>
            <p>This proposal is valid for 30 days from the date of issue.</p>
            <p>&copy; 2025 Mediaforce. All rights reserved.</p>
        </div>
    </div>
</body>
</html>'''

    return html


def extract_section(content, start_marker, end_marker):
    """Extract a section from AI-generated content between markers"""
    if not content:
        return '<p>Content generation in progress...</p>'

    # Try to find section by comment markers
    start_pattern = f'<!-- SECTION: {start_marker}'
    start_idx = content.find(start_pattern)

    if start_idx == -1:
        # Try alternate patterns
        start_pattern = f'<!-- {start_marker}'
        start_idx = content.find(start_pattern)

    if start_idx == -1:
        # Try finding by section header
        start_pattern = start_marker.replace('_', ' ').title()
        start_idx = content.lower().find(start_marker.lower().replace('_', ' '))

    if start_idx == -1:
        return '<p>Section content not available.</p>'

    # Find end of section
    if end_marker:
        end_pattern = f'<!-- SECTION: {end_marker}'
        end_idx = content.find(end_pattern, start_idx + len(start_pattern))
        if end_idx == -1:
            end_pattern = f'<!-- {end_marker}'
            end_idx = content.find(end_pattern, start_idx + len(start_pattern))
        if end_idx == -1:
            end_idx = content.lower().find(end_marker.lower().replace('_', ' '), start_idx + 50)
    else:
        end_idx = len(content)

    if end_idx == -1:
        end_idx = len(content)

    # Extract and clean the section
    section = content[start_idx:end_idx]

    # Remove the comment marker if present
    section = re.sub(r'<!--[^>]*-->', '', section)
    section = section.strip()

    # If section starts with a header matching the section name, remove it (we add our own h2)
    section = re.sub(r'^<h[23][^>]*>[^<]*</h[23]>\s*', '', section, flags=re.IGNORECASE)

    return section if section else '<p>Section content not available.</p>'


def generate_ai_proposal(text, data):
    """Use Claude API to generate rich proposal content"""
    if not HAS_ANTHROPIC:
        return None

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return None

    client = Anthropic(api_key=api_key)

    company = data['company'] or 'the client'
    industry = data['industry'] or 'their industry'
    location = data['location'] or ''
    challenges = data['challenges'] or ['increase online visibility', 'generate more leads']
    goals = data['goals'] or ['grow website traffic', 'increase qualified leads']
    budget = data['budget_num']
    services = data['services']

    # Build services string
    services_str = ', '.join(services) if services else 'Google Ads and SEO'

    system_message = """You are an expert digital marketing strategist writing proposals for Mediaforce, a Canadian digital marketing agency. Generate professional, persuasive, detailed proposal content.

Your writing style:
- Confident and authoritative but not arrogant
- Data-driven and specific
- Client-focused (emphasize their success)
- Use concrete examples and specific tactics
- Professional but engaging tone

Output clean HTML with these allowed tags only: p, h3, h4, ul, li, strong, em, div
Use these CSS classes: info-box, card-grid, card, success-box, warning-box"""

    prompt = f"""Generate a complete digital marketing proposal for:

**Client:** {company}
**Industry:** {industry}
**Location:** {location}
**Budget:** ${budget:,}/month
**Services Needed:** {services_str}

**Their Challenges:**
{chr(10).join('- ' + c for c in challenges)}

**Their Goals:**
{chr(10).join('- ' + g for g in goals)}

**Original Client Brief:**
{text}

Generate the following sections with rich, specific, persuasive content (output raw HTML):

1. EXECUTIVE SUMMARY (100-150 words)
- Opening paragraph positioning the client
- Info-box with "This Proposal Delivers:" containing 5-6 bullet points of outcomes

2. UNDERSTANDING YOUR BUSINESS (200-250 words)
- Their current situation and challenges
- Card grid with 3 challenge cards
- Target audience description

3. YOUR GOALS & VISION (150-200 words)
- Two cards: Short-term goals (3-6 months) and Long-term vision (1-3 years)
- Each with 4-5 specific bullet points

4. OUR STRATEGY & APPROACH (300-400 words)
- Platform recommendation (why Google Ads/SEO/Social works for them)
- Card grid with service-specific tactics:
  - If Google Ads: keyword strategy, ad types, targeting approach
  - If SEO: technical SEO, content strategy, local SEO
  - If Social: platform selection, audience targeting, creative approach
- Campaign structure overview

5. IMPLEMENTATION TIMELINE (100-150 words)
- 4 timeline items: Week 1, Week 2, Week 3, Ongoing
- Each with title and 2-3 bullet points

6. INVESTMENT & ROI (150-200 words)
Based on ${budget:,}/month total:
- Management fee: ${min(899, budget//3)}/month
- Ad spend: ${budget - min(899, budget//3)}/month
- What's included (5-6 bullet points)
- Why this investment makes sense

7. NEXT STEPS (100 words)
- 3 steps to get started
- Contact call-to-action

Output each section with a clear HTML comment like <!-- SECTION: EXECUTIVE SUMMARY --> before each section.
Make the content specific to {company} and {industry}. Reference their actual challenges and goals.
Be persuasive about why Mediaforce is the right partner."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            system=system_message,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"AI generation error: {e}")
        return None


def generate_proposal_from_text(text):
    """Generate full BMW-style proposal HTML from parsed text"""
    data = parse_client_text(text)

    # Try AI generation first
    ai_content = generate_ai_proposal(text, data)

    company = data['company'] or 'Your Company'
    industry = data['industry'] or 'Your Industry'
    location = data['location'] or ''
    challenges = data['challenges'] or ['Increase online visibility', 'Generate more leads', 'Improve conversion rates']
    goals = data['goals'] or ['Grow website traffic', 'Increase qualified leads', 'Boost revenue']
    budget = data['budget_num']
    services = data['services']

    # Calculate pricing
    management_fee = min(899, budget // 3) if budget > 1500 else 499
    ad_spend = budget - management_fee

    today = datetime.now().strftime('%B %d, %Y')

    # If AI content was generated, use it
    if ai_content:
        return build_proposal_with_ai_content(company, industry, location, budget, management_fee, ad_spend, today, ai_content, services)

    # Fallback to template-based generation
    data['company'] = company
    data['industry'] = industry
    data['location'] = location
    data['challenges'] = challenges
    data['goals'] = goals
    data['budget_num'] = budget
    data['services'] = services

    company = data['company'] or 'Your Company'
    industry = data['industry'] or 'Your Industry'
    location = data['location'] or ''
    challenges = data['challenges'] or ['Increase online visibility', 'Generate more leads', 'Improve conversion rates']
    goals = data['goals'] or ['Grow website traffic', 'Increase qualified leads', 'Boost revenue']
    budget = data['budget_num']
    services = data['services']

    # Calculate pricing
    management_fee = 899 if budget < 3000 else 1200 if budget < 5000 else 1500
    ad_spend = budget - management_fee if budget > management_fee else 1500

    # Determine which services sections to show
    has_google_ads = any('google' in s.lower() or 'ads' in s.lower() or 'ppc' in s.lower() or 'sem' in s.lower() for s in services)
    has_seo = any('seo' in s.lower() or 'organic' in s.lower() or 'search engine opt' in s.lower() for s in services)
    has_social = any('social' in s.lower() or 'facebook' in s.lower() or 'instagram' in s.lower() or 'linkedin' in s.lower() for s in services)

    if not has_google_ads and not has_seo and not has_social:
        has_google_ads = True
        has_seo = True

    today = datetime.now().strftime('%B %d, %Y')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Marketing Proposal - {company}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            background: #fff;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 0; }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}
        .header img {{ height: 50px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 2.2rem; font-weight: 600; margin-bottom: 10px; }}
        .header .subtitle {{ font-size: 1.1rem; opacity: 0.9; }}
        .header .date {{ margin-top: 20px; font-size: 0.9rem; opacity: 0.8; }}

        /* Sections */
        .section {{ padding: 40px; }}
        .section-alt {{ background: #f8f9fa; }}
        .section-blue {{ background: #e8f4fc; }}
        .section h2 {{
            color: #0e5881;
            font-size: 1.4rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #ffcc33;
        }}

        /* Cards */
        .card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .card h3 {{ color: #0e5881; font-size: 1.1rem; margin-bottom: 12px; }}
        .card ul {{ padding-left: 20px; }}
        .card li {{ margin: 8px 0; }}

        /* Info Box */
        .info-box {{
            background: #e8f4fc;
            border-left: 4px solid #0e5881;
            padding: 20px;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
        }}

        /* Price Box */
        .price-section {{ background: #0e5881; color: white; padding: 50px 40px; text-align: center; }}
        .price-section h2 {{ color: white; border-bottom-color: #ffcc33; }}
        .price-box {{
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 30px;
            margin: 30px auto;
            max-width: 500px;
        }}
        .price {{ font-size: 3rem; font-weight: 700; color: #ffcc33; }}
        .price-detail {{ margin-top: 15px; opacity: 0.9; }}

        /* Timeline */
        .timeline {{ margin-top: 20px; }}
        .timeline-item {{
            display: flex;
            margin-bottom: 15px;
            align-items: flex-start;
        }}
        .timeline-week {{
            background: #0e5881;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            min-width: 80px;
            text-align: center;
            margin-right: 15px;
        }}
        .timeline-content {{ flex: 1; }}
        .timeline-content h4 {{ color: #0e5881; margin-bottom: 5px; }}

        /* Services Icons */
        .service-icon {{
            width: 60px;
            height: 60px;
            background: #e8f4fc;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }}

        /* Footer */
        .footer {{
            background: #0e5881;
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .footer h2 {{ color: white; border: none; margin-bottom: 20px; }}
        .contact-info {{ display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; }}
        .contact-item {{ display: flex; align-items: center; gap: 10px; }}

        /* Mobile */
        @media (max-width: 768px) {{
            .header {{ padding: 40px 20px; }}
            .header h1 {{ font-size: 1.6rem; }}
            .section {{ padding: 30px 20px; }}
            .card-grid {{ grid-template-columns: 1fr; }}
            .price {{ font-size: 2.2rem; }}
            .contact-info {{ flex-direction: column; gap: 15px; }}
        }}

        @media print {{
            .section {{ page-break-inside: avoid; }}
            .price-section {{ page-break-before: always; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <img src="https://mediaforce.ca/wp-content/uploads/2025/10/mf-logo2.png" alt="Mediaforce">
            <h1>Digital Marketing Proposal</h1>
            <div class="subtitle">Prepared for {company}</div>
            <div class="date">{today}</div>
        </div>

        <!-- Understanding Your Business -->
        <div class="section">
            <h2>Understanding Your Business</h2>
            <div class="info-box">
                <strong>{company}</strong>'''

    if industry:
        html += f'<br>Industry: {industry}'
    if location:
        html += f'<br>Location: {location}'

    html += f'''
            </div>

            <h3 style="color: #0e5881; margin: 25px 0 15px;">Current Challenges</h3>
            <ul>'''

    for challenge in challenges[:5]:
        html += f'<li>{challenge}</li>'

    html += '''
            </ul>
        </div>

        <!-- Your Goals -->
        <div class="section section-alt">
            <h2>Your Vision for Success</h2>
            <div class="card-grid">
                <div class="card">
                    <div class="service-icon">🎯</div>
                    <h3>Short-Term Goals</h3>
                    <ul>'''

    for goal in goals[:3]:
        html += f'<li>{goal}</li>'

    html += '''
                    </ul>
                </div>
                <div class="card">
                    <div class="service-icon">🚀</div>
                    <h3>Long-Term Vision</h3>
                    <ul>
                        <li>Sustainable growth and market leadership</li>
                        <li>Strong digital brand presence</li>
                        <li>Predictable lead generation</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Our Approach -->
        <div class="section section-blue">
            <h2>Our Approach & Strategy</h2>
            <div class="card-grid">'''

    if has_google_ads:
        html += '''
                <div class="card">
                    <img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png" height="40" alt="Google Ads" style="margin-bottom: 15px;">
                    <h3>Google Ads Management</h3>
                    <ul>
                        <li>Strategic keyword targeting</li>
                        <li>Compelling ad copy creation</li>
                        <li>Landing page optimization</li>
                        <li>Conversion tracking setup</li>
                        <li>Ongoing bid optimization</li>
                    </ul>
                </div>'''

    if has_seo:
        html += '''
                <div class="card">
                    <div class="service-icon">🔍</div>
                    <h3>AI-Friendly SEO</h3>
                    <ul>
                        <li>Technical SEO audit & fixes</li>
                        <li>Content optimization</li>
                        <li>Local SEO enhancement</li>
                        <li>Link building outreach</li>
                        <li>Monthly ranking reports</li>
                    </ul>
                </div>'''

    if has_social:
        html += '''
                <div class="card">
                    <div class="service-icon">📱</div>
                    <h3>Paid Social Media</h3>
                    <ul>
                        <li>Facebook & Instagram Ads</li>
                        <li>LinkedIn advertising</li>
                        <li>Audience targeting</li>
                        <li>Creative development</li>
                        <li>Performance optimization</li>
                    </ul>
                </div>'''

    html += '''
            </div>
        </div>

        <!-- Timeline -->
        <div class="section">
            <h2>Implementation Timeline</h2>
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-week">Week 1</div>
                    <div class="timeline-content">
                        <h4>Discovery & Setup</h4>
                        <p>Kickoff call, account access, tracking setup, strategy alignment</p>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-week">Week 2</div>
                    <div class="timeline-content">
                        <h4>Strategy & Creative</h4>
                        <p>Campaign structure, keyword research, ad copy development</p>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-week">Week 3</div>
                    <div class="timeline-content">
                        <h4>Launch & Optimize</h4>
                        <p>Campaign launch, initial optimizations, performance monitoring</p>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-week">Ongoing</div>
                    <div class="timeline-content">
                        <h4>Continuous Improvement</h4>
                        <p>Weekly optimizations, A/B testing, scaling winning campaigns</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Investment -->
        <div class="price-section">
            <h2>Your Investment</h2>
            <div class="price-box">'''

    if has_google_ads:
        html += '''
                <img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png" height="40" alt="Google Ads" style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 20px;">'''

    html += f'''
                <div class="price">${budget:,}/month</div>
                <div class="price-detail">
                    Management Fee: ${management_fee:,}/mo<br>
                    Ad Spend: ${ad_spend:,}/mo
                </div>
            </div>
            <p style="opacity: 0.9; max-width: 500px; margin: 0 auto;">
                Includes full campaign management, creative services, weekly reporting, and dedicated account support.
            </p>
        </div>

        <!-- Next Steps -->
        <div class="footer">
            <h2>Ready to Get Started?</h2>
            <p style="margin-bottom: 25px;">Let's schedule a call to discuss your goals and answer any questions.</p>
            <div class="contact-info">
                <div class="contact-item">📧 jbon@mediaforce.ca</div>
                <div class="contact-item">📞 613 265 2120</div>
                <div class="contact-item">🌐 mediaforce.ca</div>
            </div>
        </div>
    </div>
</body>
</html>'''

    return html


def generate_simple_preview(data):
    """Generate a simple HTML preview from form data"""
    client_name = data.get('client_name', 'Client')
    industry = data.get('industry', '')

    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Proposal for {client_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px; color: #333; }}
        .header {{ background: #0e5881; color: white; padding: 40px; text-align: center; margin: -40px -40px 40px; }}
        .header h1 {{ margin: 0; font-size: 2rem; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
        .section h2 {{ color: #0e5881; margin-top: 0; border-bottom: 2px solid #ffcc33; padding-bottom: 10px; }}
        .info-box {{ background: #e8f4fc; padding: 15px; border-radius: 6px; margin: 15px 0; }}
        .price-box {{ background: #0e5881; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .price {{ font-size: 2rem; font-weight: bold; color: #ffcc33; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <img src="https://mediaforce.ca/wp-content/uploads/2025/10/mf-logo2.png" height="50" alt="Mediaforce">
        <h1>Digital Marketing Proposal</h1>
        <p>Prepared for {client_name}</p>
    </div>

    <div class="section">
        <h2>Understanding Your Business</h2>
        <div class="info-box">
            <strong>Industry:</strong> {industry}<br>
            <strong>Location:</strong> {data.get('location', 'N/A')}
        </div>
        <p><strong>Current Challenges:</strong></p>
        <ul>'''

    pain_points = data.get('pain_points', '').split('\n') if data.get('pain_points') else ['Increase online visibility']
    for point in pain_points:
        if point.strip():
            html += f'<li>{point.strip()}</li>'

    html += '''</ul>
    </div>

    <div class="section">
        <h2>Your Goals</h2>
        <p><strong>Short-Term (3-6 months):</strong></p>
        <ul>'''

    short_goals = data.get('short_term_goals', '').split('\n') if data.get('short_term_goals') else ['Increase traffic']
    for goal in short_goals:
        if goal.strip():
            html += f'<li>{goal.strip()}</li>'

    html += '''</ul>
    </div>

    <div class="section">
        <h2>Investment</h2>
        <div class="price-box">
            <p>Monthly Investment</p>'''

    retainer = int(data.get('monthly_retainer', 899) or 899)
    ad_spend = int(data.get('ad_spend', 1500) or 1500)
    total = retainer + ad_spend

    html += f'''<div class="price">${total:,}/month</div>
            <p>Management Fee: ${retainer:,} | Ad Spend: ${ad_spend:,}</p>
        </div>
    </div>

    <div class="section" style="text-align: center;">
        <h2>Next Steps</h2>
        <p>Ready to get started? Contact us:</p>
        <p>
            <strong>Email:</strong> jbon@mediaforce.ca<br>
            <strong>Phone:</strong> 613 265 2120<br>
            <strong>Website:</strong> mediaforce.ca
        </p>
    </div>
</body>
</html>'''

    return html


def build_metadata_from_form(form):
    """Convert form data to metadata structure"""

    # Parse services
    services = {
        'google_ads': {
            'enabled': form.get('google_ads_enabled') == 'on',
            'monthly_budget': int(form.get('google_ads_budget', 0) or 0)
        },
        'seo': {
            'enabled': form.get('seo_enabled') == 'on',
            'monthly_fee': int(form.get('seo_fee', 0) or 0)
        },
        'paid_social': {
            'enabled': form.get('paid_social_enabled') == 'on',
            'monthly_budget': int(form.get('paid_social_budget', 0) or 0),
            'platforms': form.getlist('social_platforms')
        }
    }

    metadata = {
        'metadata': {
            'client_name': form.get('client_name', ''),
            'proposal_date': form.get('proposal_date', datetime.now().strftime('%Y-%m-%d')),
            'analyst': form.get('analyst', 'The Mediaforce Team'),
            'proposal_type': 'Digital Marketing Strategy Proposal'
        },
        'client_context': {
            'industry': form.get('industry', ''),
            'brands': [b.strip() for b in form.get('brands', '').split(',') if b.strip()],
            'location': form.get('location', ''),
            'current_situation': {
                'description': form.get('situation_description', ''),
                'pain_points': [p.strip() for p in form.get('pain_points', '').split('\n') if p.strip()]
            },
            'success_definition': {
                'short_term': [g.strip() for g in form.get('short_term_goals', '').split('\n') if g.strip()],
                'long_term': [g.strip() for g in form.get('long_term_goals', '').split('\n') if g.strip()]
            },
            'target_audience': {
                'demographics': [d.strip() for d in form.get('demographics', '').split('\n') if d.strip()],
                'psychographics': [p.strip() for p in form.get('psychographics', '').split('\n') if p.strip()],
                'behaviors': [b.strip() for b in form.get('behaviors', '').split('\n') if b.strip()]
            }
        },
        'competitive_landscape': {
            'market_overview': form.get('market_overview', ''),
            'competitors': parse_competitors(form.get('competitors', '')),
            'opportunities': [o.strip() for o in form.get('opportunities', '').split('\n') if o.strip()]
        },
        'strategy': {
            'pillars': services
        },
        'investment': {
            'packages': [{
                'name': 'DIGITAL MARKETING PACKAGE',
                'monthly_retainer': int(form.get('monthly_retainer', 0) or 0),
                'ad_spend': int(form.get('ad_spend', 0) or 0),
                'total_monthly': int(form.get('monthly_retainer', 0) or 0) + int(form.get('ad_spend', 0) or 0)
            }]
        },
        'next_steps': {
            'contact': {
                'name': 'Mediaforce Team',
                'email': 'jbon@mediaforce.ca',
                'phone': '613 265 2120',
                'website': 'mediaforce.ca'
            }
        }
    }

    return metadata


def parse_competitors(competitors_text):
    """Parse competitors from text input"""
    competitors = []
    for line in competitors_text.split('\n'):
        line = line.strip()
        if line:
            competitors.append({
                'name': line,
                'strengths': [],
                'weaknesses': []
            })
    return competitors


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
