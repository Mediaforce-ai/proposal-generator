"""
Mediaforce Proposal Generator - Web Application
Flask-based web interface for staff to create proposals
"""

import os
import json
import secrets
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from authlib.integrations.flask_client import OAuth

# Import proposal generation modules
from generator import ProposalGenerator
from assembler import ProposalAssembler

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

        # Generate proposal using the assembler
        assembler = ProposalAssembler()
        html_content = assembler.generate(metadata)

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

        # Use template-based generation for preview
        assembler = ProposalAssembler()
        preview_html = assembler.generate_preview(metadata)

        return jsonify({
            'success': True,
            'html': preview_html
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
