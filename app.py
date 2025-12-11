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
    """Build the full proposal HTML with AI-generated content"""

    # Determine service badges
    has_google_ads = any('google' in s.lower() or 'ads' in s.lower() or 'ppc' in s.lower() for s in services)
    has_seo = any('seo' in s.lower() for s in services)
    has_social = any('social' in s.lower() or 'facebook' in s.lower() or 'instagram' in s.lower() for s in services)

    service_badges = []
    if has_google_ads:
        service_badges.append('<img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png" height="30" alt="Google Ads" style="margin-right: 10px;">')
    if has_seo:
        service_badges.append('<span style="background: #0e5881; color: white; padding: 5px 12px; border-radius: 4px; font-size: 12px; margin-right: 10px;">SEO</span>')
    if has_social:
        service_badges.append('<span style="background: #0e5881; color: white; padding: 5px 12px; border-radius: 4px; font-size: 12px;">Social</span>')

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
            line-height: 1.7;
            color: #333;
            background: #fff;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 0; }}

        /* Cover */
        .cover {{
            background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%);
            color: white;
            padding: 80px 40px;
            text-align: center;
        }}
        .cover img {{ height: 60px; margin-bottom: 30px; }}
        .cover h1 {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 15px; }}
        .cover .subtitle {{ font-size: 1.3rem; opacity: 0.95; margin-bottom: 10px; }}
        .cover .date {{ font-size: 0.95rem; opacity: 0.8; margin-top: 30px; }}
        .cover .services {{ margin-top: 25px; display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 10px; }}

        /* Sections */
        .section {{ padding: 50px 40px; }}
        .section-alt {{ background: #f8f9fa; }}
        .section-blue {{ background: #e8f4fc; }}
        .section h2 {{
            color: #0e5881;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 25px;
            padding-bottom: 12px;
            border-bottom: 3px solid #ffcc33;
        }}
        .section h3 {{ color: #0e5881; font-size: 1.2rem; margin: 25px 0 15px; }}
        .section h4 {{ color: #0e5881; font-size: 1rem; margin: 20px 0 10px; }}
        .section p {{ margin-bottom: 15px; }}
        .section ul {{ padding-left: 25px; margin-bottom: 15px; }}
        .section li {{ margin: 8px 0; }}

        /* Info Box */
        .info-box {{
            background: #e8f4fc;
            border-left: 4px solid #0e5881;
            padding: 20px 25px;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
        }}
        .info-box h4 {{ color: #0e5881; margin-top: 0; margin-bottom: 12px; }}

        .success-box {{
            background: #e8f5e9;
            border-left: 4px solid #28a745;
            padding: 20px 25px;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
        }}
        .success-box h4 {{ color: #28a745; margin-top: 0; margin-bottom: 12px; }}

        .warning-box {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 20px 25px;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
        }}
        .warning-box h4 {{ color: #e65100; margin-top: 0; margin-bottom: 12px; }}

        /* Cards */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
        }}
        .card h4 {{ color: #0e5881; margin-top: 0; margin-bottom: 12px; font-size: 1.05rem; }}
        .card ul {{ padding-left: 18px; }}
        .card li {{ margin: 6px 0; font-size: 0.95rem; }}
        .card p {{ font-size: 0.95rem; margin-bottom: 10px; }}

        /* Price Section */
        .price-section {{
            background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}
        .price-section h2 {{ color: white; border-bottom-color: #ffcc33; display: inline-block; }}
        .price-box {{
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 35px;
            margin: 35px auto;
            max-width: 500px;
        }}
        .price {{ font-size: 3.5rem; font-weight: 700; color: #ffcc33; }}
        .price-detail {{ margin-top: 15px; opacity: 0.95; font-size: 1.05rem; }}

        /* Timeline */
        .timeline {{ margin: 25px 0; }}
        .timeline-item {{
            display: flex;
            margin-bottom: 20px;
            align-items: flex-start;
        }}
        .timeline-week {{
            background: #0e5881;
            color: white;
            padding: 10px 18px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.85rem;
            min-width: 90px;
            text-align: center;
            margin-right: 20px;
        }}
        .timeline-content {{ flex: 1; }}
        .timeline-content h4 {{ color: #0e5881; margin-bottom: 8px; margin-top: 0; }}

        /* Footer */
        .footer {{
            background: #0e5881;
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        .footer h2 {{ color: white; border: none; margin-bottom: 20px; }}
        .contact-info {{
            display: flex;
            justify-content: center;
            gap: 35px;
            flex-wrap: wrap;
            margin-top: 25px;
        }}
        .contact-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1.05rem;
        }}

        /* Mobile */
        @media (max-width: 768px) {{
            .cover {{ padding: 50px 25px; }}
            .cover h1 {{ font-size: 1.8rem; }}
            .section {{ padding: 35px 25px; }}
            .card-grid {{ grid-template-columns: 1fr; }}
            .price {{ font-size: 2.5rem; }}
            .contact-info {{ flex-direction: column; gap: 15px; }}
            .timeline-item {{ flex-direction: column; }}
            .timeline-week {{ margin-bottom: 10px; }}
        }}

        @media print {{
            .section {{ page-break-inside: avoid; }}
            .price-section {{ page-break-before: always; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Cover -->
        <div class="cover">
            <img src="https://mediaforce.ca/wp-content/uploads/2025/10/mf-logo2.png" alt="Mediaforce">
            <h1>Digital Marketing Proposal</h1>
            <div class="subtitle">Prepared for {company}</div>
            <div class="services">{''.join(service_badges)}</div>
            <div class="date">{today}</div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2>Executive Summary</h2>
            {extract_section(ai_content, 'EXECUTIVE SUMMARY', 'UNDERSTANDING YOUR BUSINESS')}
        </div>

        <!-- Understanding Your Business -->
        <div class="section section-alt">
            <h2>Understanding Your Business</h2>
            {extract_section(ai_content, 'UNDERSTANDING YOUR BUSINESS', 'YOUR GOALS')}
        </div>

        <!-- Goals & Vision -->
        <div class="section">
            <h2>Your Goals & Vision for Success</h2>
            {extract_section(ai_content, 'YOUR GOALS', 'OUR STRATEGY')}
        </div>

        <!-- Strategy -->
        <div class="section section-blue">
            <h2>Our Strategy & Approach</h2>
            {extract_section(ai_content, 'OUR STRATEGY', 'IMPLEMENTATION')}
        </div>

        <!-- Timeline -->
        <div class="section">
            <h2>Implementation Timeline</h2>
            {extract_section(ai_content, 'IMPLEMENTATION', 'INVESTMENT')}
        </div>

        <!-- Investment -->
        <div class="price-section">
            <h2>Your Investment</h2>
            <div class="price-box">
                {''.join(service_badges)}
                <div class="price" style="margin-top: 20px;">${budget:,}/month</div>
                <div class="price-detail">
                    Management Fee: ${management_fee:,}/mo | Ad Spend: ${ad_spend:,}/mo
                </div>
            </div>
            {extract_section(ai_content, 'INVESTMENT', 'NEXT STEPS')}
        </div>

        <!-- Next Steps -->
        <div class="footer">
            <h2>Ready to Get Started?</h2>
            {extract_section(ai_content, 'NEXT STEPS', None)}
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
