#!/usr/bin/env python3
"""
Assemble final HTML proposal from generated sections
"""

import json
from pathlib import Path
from datetime import datetime

def load_proposal_data():
    """Load generated proposal sections"""
    with open('proposal_data.json', 'r') as f:
        return json.load(f)

def load_template():
    """Load HTML template from tool directory"""
    template_path = Path.home() / 'AI' / 'TOOLS' / 'mediaforce-proposal-generator' / 'templates' / 'template.html'
    with open(template_path, 'r') as f:
        return f.read()

def load_css():
    """Load CSS from tool directory"""
    css_path = Path.home() / 'AI' / 'TOOLS' / 'mediaforce-proposal-generator' / 'templates' / 'proposal.css'
    with open(css_path, 'r') as f:
        return f.read()

def assemble_html(data, template, css):
    """Assemble final HTML with all sections"""
    html = template

    # Replace metadata placeholders
    metadata = data.get('metadata', {})
    html = html.replace('{{CLIENT}}', metadata.get('client_name', 'Client Name'))
    html = html.replace('{{PROPOSAL_TYPE}}', metadata.get('proposal_type', 'Digital Marketing Proposal'))
    html = html.replace('{{ANALYST}}', metadata.get('analyst', 'The Mediaforce Team'))
    html = html.replace('{{PROPOSAL_DATE}}', metadata.get('proposal_date', datetime.now().strftime('%Y-%m-%d')))
    html = html.replace('{{YEAR}}', str(datetime.now().year))

    # Replace section slots
    html = html.replace('<!-- SLOT: EXECUTIVE_SUMMARY -->', data.get('executive_summary', '<p>Executive summary not generated</p>'))
    html = html.replace('<!-- SLOT: YOUR_BUSINESS -->', data.get('your_business', '<p>Your business section not generated</p>'))
    html = html.replace('<!-- SLOT: COMPETITIVE_ANALYSIS -->', data.get('competitive_analysis', '<p>Competitive analysis not generated</p>'))
    html = html.replace('<!-- SLOT: STRATEGY -->', data.get('strategy', '<p>Strategy not generated</p>'))
    html = html.replace('<!-- SLOT: SUCCESS_METRICS -->', data.get('success_metrics', '<p>Success metrics not generated</p>'))
    html = html.replace('<!-- SLOT: TIMELINE -->', data.get('timeline', '<p>Timeline not generated</p>'))
    html = html.replace('<!-- SLOT: INVESTMENT -->', data.get('investment', '<p>Investment not generated</p>'))
    html = html.replace('<!-- SLOT: NEXT_STEPS -->', data.get('next_steps', '<p>Next steps not generated</p>'))

    # Embed CSS (replace the link tag with inline style)
    html = html.replace('<link rel="stylesheet" href="proposal.css">', f'<style>\n{css}\n</style>')

    return html

def main():
    print("Loading proposal data...")
    data = load_proposal_data()

    print("Loading template and CSS...")
    template = load_template()
    css = load_css()

    print("Assembling final HTML...")
    html = assemble_html(data, template, css)

    # Write final proposal
    output_path = 'Proposal.html'
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ Proposal generated successfully!")
    print(f"📁 Location: {Path.cwd() / output_path}")
    print(f"\nOpen with: open {output_path}")

if __name__ == '__main__':
    main()
