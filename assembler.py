#!/usr/bin/env python3
"""
Proposal Assembler - Inserts generated fragments into BMW-style template
"""

from pathlib import Path
from typing import Dict
from datetime import datetime


class ProposalAssembler:
    """Assembles validated fragments into final HTML"""

    def __init__(self, template_path: Path, css_path: Path):
        with open(template_path) as f:
            self.template = f.read()

        with open(css_path) as f:
            self.css = f.read()

    def assemble(self, data: Dict) -> str:
        """Assemble final HTML from generated fragments"""

        html = self.template

        # Replace metadata placeholders
        metadata = data.get('metadata', {})
        html = html.replace('{{CLIENT}}', metadata.get('client_name', 'Client Name'))
        html = html.replace('{{PROPOSAL_TYPE}}', metadata.get('proposal_type', 'Digital Marketing Proposal'))
        html = html.replace('{{ANALYST}}', metadata.get('analyst', 'The Mediaforce Team'))
        html = html.replace('{{PROPOSAL_DATE}}', metadata.get('proposal_date', datetime.now().strftime('%Y-%m-%d')))
        html = html.replace('{{YEAR}}', str(datetime.now().year))

        # Replace section slots
        html = html.replace(
            '<!-- SLOT: EXECUTIVE_SUMMARY -->',
            data.get('executive_summary', '<p>Executive summary not generated</p>')
        )

        html = html.replace(
            '<!-- SLOT: YOUR_BUSINESS -->',
            data.get('your_business', '<p>Your business section not generated</p>')
        )

        html = html.replace(
            '<!-- SLOT: COMPETITIVE_ANALYSIS -->',
            data.get('competitive_analysis', '<p>Competitive analysis not generated</p>')
        )

        html = html.replace(
            '<!-- SLOT: STRATEGY -->',
            data.get('strategy', '<p>Strategy section not generated</p>')
        )

        html = html.replace(
            '<!-- SLOT: SUCCESS_METRICS -->',
            data.get('success_metrics', '<p>Success metrics not generated</p>')
        )

        html = html.replace(
            '<!-- SLOT: TIMELINE -->',
            data.get('timeline', '<p>Timeline not generated</p>')
        )

        html = html.replace(
            '<!-- SLOT: INVESTMENT -->',
            data.get('investment', '<p>Investment section not generated</p>')
        )

        html = html.replace(
            '<!-- SLOT: NEXT_STEPS -->',
            data.get('next_steps', '<p>Next steps not generated</p>')
        )

        # Embed CSS
        html = html.replace('<link rel="stylesheet" href="proposal.css">', f'<style>{self.css}</style>')

        return html


def main():
    """Test assembler"""
    import json

    # Create test data
    test_data = {
        'metadata': {
            'client_name': 'Test Corp',
            'analyst': 'The Mediaforce Team',
            'proposal_date': '2025-11-04',
            'proposal_type': 'Digital Marketing Strategy Proposal'
        },
        'executive_summary': '<p>Test executive summary</p>',
        'your_business': '<h3>Test Your Business</h3><p>Content here</p>',
        'competitive_analysis': '<h3>Test Analysis</h3>',
        'strategy': '<h2>Test Strategy</h2>',
        'success_metrics': '<h3>Test Metrics</h3>',
        'timeline': '<h4>Week 1</h4><p>Test timeline</p>',
        'investment': '<div class="price-box"><h3>$25,000/month</h3></div>',
        'next_steps': '<h4>Getting Started</h4><p>Contact us</p>'
    }

    assembler = ProposalAssembler(
        Path(__file__).parent / 'templates' / 'template.html',
        Path(__file__).parent / 'templates' / 'proposal.css'
    )

    html = assembler.assemble(test_data)

    output_file = Path(__file__).parent / 'test_output.html'
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✓ Test proposal generated: {output_file}")
    print(f"  Size: {len(html)} characters")


if __name__ == '__main__':
    main()
