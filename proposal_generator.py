#!/usr/bin/env python3
"""
Mediaforce Proposal Generator
Generates BMW-style digital marketing proposals using Claude AI
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from anthropic import Anthropic


# Global system message for all LLM calls
SYSTEM_MESSAGE = """You are generating HTML fragments for a digital marketing proposal.

**ALLOWED TAGS:** p, h2, h3, h4, ul, ol, li, strong, em, div, span, br, table, thead, tbody, tr, th, td, svg, img

**ALLOWED CLASSES:** section, info-box, warning-box, success-box, highlight-box, critical-box, checklist, card-grid, card, price-box, gradient-text, section-icon, platform-logo-section, platform-badge, platform-badge-text

**OFFICIAL ASSET URLS:**
- Google Ads Logo: https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png
- Mediaforce Logo: https://mediaforce.ca/wp-content/uploads/2025/10/mf-logo2.png

**PLATFORM LOGOS:**
- Use platform-logo-section and platform-badge classes for platform branding
- Example: <div class="platform-badge"><img src="[URL]" alt="Platform Name" style="height: 40px; width: auto;"><span class="platform-badge-text">Powered by [Platform]</span></div>

**RULES:**
- Do NOT use style attributes except for platform logo sizing (height: 40px; width: auto;)
- Do NOT use script tags
- Do NOT invent new classes beyond those listed
- Produce professional, persuasive, client-focused content
- Respect the provided length budget
- Output ONLY the requested HTML fragment
- Do NOT include explanations, comments, or markdown code fences
- Output raw HTML ready for direct insertion
- Use <ul class="checklist"> for checkmark lists
- Wrap key deliverables in <div class="success-box"> or <div class="info-box">"""


class ProposalGenerator:
    """Generates complete digital marketing proposals from metadata"""

    def __init__(self, project_dir: Path, api_key: str):
        self.project_dir = Path(project_dir)
        self.client = Anthropic(api_key=api_key)
        self.proposal_data = {}

    def load_metadata(self) -> Dict[str, Any]:
        """Load proposal metadata from JSON file"""
        metadata_file = self.project_dir / 'metadata.json'

        if not metadata_file.exists():
            print("\n❌ ERROR: metadata.json not found!")
            print(f"   Expected location: {metadata_file}")
            print("\n   See metadata_schema.json for the required format")
            raise FileNotFoundError(f"metadata.json required at {metadata_file}")

        with open(metadata_file) as f:
            return json.load(f)

    def call_claude(self, prompt: str, max_tokens: int = 4000) -> str:
        """Make API call to Claude"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=max_tokens,
            system=SYSTEM_MESSAGE,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text

    # ==================== SECTION GENERATORS ====================

    def generate_executive_summary(self, data: Dict) -> str:
        """Generate executive summary section"""
        print("[Generating Executive Summary]")

        metadata = data['metadata']
        client_context = data.get('client_context', {})

        prompt = f"""**Client:** {metadata['client_name']}
**Industry:** {client_context.get('industry', 'N/A')}
**Brands:** {', '.join(client_context.get('brands', []))}

**Task:** Write an executive summary for this digital marketing proposal.

**Structure:**
1. Opening paragraph (3-4 sentences): Position the client as a leader in their industry, acknowledge their brand excellence, and state that they deserve a digital marketing partner who understands their market and executes with precision.

2. Success box with "This Proposal Delivers:" heading containing 5-7 bullet points of key outcomes (use <ul class="checklist">)

3. Info box with "Expected Outcome:" describing measurable results within 3-6 months

**Tone:** Professional, confident, client-focused
**Length:** ≤ 250 words total

**Output format:**
<p>Opening paragraph...</p>

<div class="success-box">
    <h4><span class="gradient-text">This Proposal Delivers:</span></h4>
    <ul class="checklist">
        <li>Outcome 1</li>
        <li>Outcome 2</li>
    </ul>
</div>

<div class="info-box">
    <p><strong>Expected Outcome:</strong> Description of results...</p>
</div>

Generate the executive summary now:"""

        return self.call_claude(prompt, max_tokens=1500)

    def generate_your_business(self, data: Dict) -> str:
        """Generate 'Understanding Your Business' section"""
        print("[Generating Your Business Section]")

        client_context = data.get('client_context', {})
        current_sit = client_context.get('current_situation', {})
        success_def = client_context.get('success_definition', {})
        target_aud = client_context.get('target_audience', {})

        prompt = f"""**Client Context:**
Current Situation: {current_sit.get('description', 'N/A')}
Pain Points: {json.dumps(current_sit.get('pain_points', []))}
Success Definition: {json.dumps(success_def)}
Target Audience: {json.dumps(target_aud)}

**Task:** Generate the "Understanding Your Business & Challenges" section with these subsections:

1. **H3: Your Current Situation** - 2-3 sentence intro paragraph
2. **Warning box with "Pain Points with Previous Agency:"** containing 3-5 bullet points
3. **H3: What Success Looks Like** with two H4 subsections:
   - **H4: Short-Term Success (3-6 Months):** with checklist (4-5 items)
   - **H4: Long-Term Success (1-3 Years):** with checklist (4-5 items)
4. **H3: Your Target Audience** with info-box containing demographics, behaviors, and market segments

**Length:** ≤ 400 words total

**Output:**
<h3>Your Current Situation</h3>
<p>...</p>

<div class="warning-box">
    <h4>Pain Points with Previous Agency:</h4>
    <ul>
        <li><strong>Point 1</strong> - Description</li>
    </ul>
</div>

<h3>What Success Looks Like for {data['metadata']['client_name']}</h3>

<h4>Short-Term Success (3-6 Months):</h4>
<ul class="checklist">
    <li>Item 1</li>
</ul>

<h4>Long-Term Success (1-3 Years):</h4>
<ul class="checklist">
    <li>Item 1</li>
</ul>

<h3>Your Target Audience</h3>
<div class="info-box">
    <p><strong>Primary Market:</strong> ...</p>
    <p><strong>Purchase Behavior:</strong> ...</p>
</div>

Generate the section:"""

        return self.call_claude(prompt, max_tokens=2000)

    def generate_competitive_analysis(self, data: Dict) -> str:
        """Generate competitive analysis section"""
        print("[Generating Competitive Analysis]")

        comp_landscape = data.get('competitive_landscape', {})

        prompt = f"""**Market Overview:** {comp_landscape.get('market_overview', 'N/A')}
**Competitors:** {json.dumps(comp_landscape.get('competitors', []))}
**Opportunities:** {json.dumps(comp_landscape.get('opportunities', []))}

**Task:** Generate competitive analysis section with:

1. **H3: Market Landscape** - 2-3 paragraph overview
2. **H3: Primary Competitors** - Brief analysis of 2-3 competitors in table format
3. **H3: Competitive Advantages** - Why we'll win (3-5 points)
4. **H3: Market Opportunities** - Gaps we'll exploit (highlight-box with 3-5 bullet points)

**Tone:** Analytical, strategic, confident
**Length:** ≤ 400 words

Generate the analysis:"""

        return self.call_claude(prompt, max_tokens=2000)

    def generate_strategy(self, data: Dict) -> str:
        """Generate our approach/strategy section"""
        print("[Generating Strategy Section]")

        strategy = data.get('strategy', {})
        pillars = strategy.get('pillars', {})

        prompt = f"""**Strategy Data:** {json.dumps(strategy, indent=2)}

**Task:** Generate comprehensive "Our Approach" section covering:

1. **H3: Our Strategic Approach** - Intro paragraph
2. **Platform Branding** - If Google Ads is enabled, include: <div class="platform-logo-section"><div class="platform-badge"><img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png" alt="Google Ads" style="height: 40px; width: auto;"><span class="platform-badge-text">Powered by Google Ads</span></div></div>
3. **H2: 1. Google Ads Strategy** (if enabled) with:
   - Campaign breakdowns by brand/budget
   - H3: Tactics (bulleted list)
   - H4: Expected Results (in 90 days)
4. **H2: 2. SEO Strategy** (if enabled) with:
   - H4: Local SEO, On-Page, Off-Page sections
   - H4: Expected Results (3-6 months)
5. **H2: 3. Paid Social Strategy** (if enabled) with:
   - Campaign structure by platform
   - H3: Tactics
   - H4: Expected Results (90 days)
6. **H3: Creative Asset Development** - What creative services are included

**Length:** ≤ 800 words total
**Tone:** Strategic, specific, results-focused

Generate the strategy section:"""

        return self.call_claude(prompt, max_tokens=4000)

    def generate_success_metrics(self, data: Dict) -> str:
        """Generate success metrics and ROI section"""
        print("[Generating Success Metrics]")

        metrics = data.get('success_metrics', {})

        prompt = f"""**Metrics Data:** {json.dumps(metrics, indent=2)}

**Task:** Generate "Success Metrics & ROI" section with:

1. **H3: Key Performance Indicators (KPIs)** - List primary KPIs
2. **H3: Reporting Cadence** - How often we report (weekly, monthly, quarterly)
3. **H3: Conservative Performance Projections** - Table showing Month 1-3, 4-6, 7-12 projections
4. **H3: ROI Calculation Example** - Specific calculation showing return on investment

**Include:** Success-box highlighting why projections are conservative and achievable

**Length:** ≤ 500 words
**Tone:** Data-driven, transparent, confident

Generate the metrics section:"""

        return self.call_claude(prompt, max_tokens=2500)

    def generate_timeline(self, data: Dict) -> str:
        """Generate implementation timeline"""
        print("[Generating Timeline]")

        timeline = data.get('timeline', {})

        prompt = f"""**Timeline Data:** {json.dumps(timeline, indent=2)}

**Task:** Generate "Implementation Timeline" section showing week-by-week rollout:

**Structure:** For each week/phase:
- **H4: Week X: Phase Name**
- Info-box with bulleted list of deliverables

**Phases to cover:**
1. Week 1: Onboarding & Discovery
2. Week 2: Strategy & Setup
3. Week 3: Creative Development
4. Week 4: Campaign Launch
5. Weeks 5-12: Optimization & Scaling

**Length:** ≤ 300 words
**Tone:** Clear, organized, actionable

Generate the timeline:"""

        return self.call_claude(prompt, max_tokens=1500)

    def generate_investment(self, data: Dict) -> str:
        """Generate investment/pricing section"""
        print("[Generating Investment Section]")

        investment = data.get('investment', {})
        packages = investment.get('packages', [])

        prompt = f"""**Investment Data:** {json.dumps(investment, indent=2)}

**Task:** Generate "Investment" section with pricing packages:

**Structure:**
1. For each package: price-box containing:
   - H3: Package name
   - Large price display
   - Description
   - Bulleted list of what's included

2. **H3: What's Included** - Detailed breakdown of deliverables across:
   - Strategy & Planning
   - Campaign Management
   - Creative Services
   - Analytics & Reporting

3. **H3: Our Commitment** - Success-box with 4-5 commitments about service quality

**Length:** ≤ 500 words
**Tone:** Value-focused, transparent, commitment-oriented

Generate the investment section:"""

        return self.call_claude(prompt, max_tokens=2500)

    def generate_next_steps(self, data: Dict) -> str:
        """Generate next steps/call-to-action"""
        print("[Generating Next Steps]")

        next_steps = data.get('next_steps', {})
        contact = next_steps.get('contact', {})

        prompt = f"""**Contact Info:** {json.dumps(contact)}
**Process:** {json.dumps(next_steps.get('process', []))}

**Task:** Generate "Next Steps" section with:

1. **H4: Getting Started** - 3-step process (numbered list)
2. **H3: Ready to Transform Your Digital Marketing?** - Compelling CTA paragraph
3. **H4: Questions or Ready to Proceed?** - Contact information in info-box

**Length:** ≤ 200 words
**Tone:** Encouraging, clear, actionable

Generate next steps:"""

        return self.call_claude(prompt, max_tokens=1000)

    # ==================== MAIN GENERATION ====================

    def generate(self, output_file: Path):
        """Main generation pipeline"""
        print("🚀 Starting Proposal Generation")
        print(f"📂 Project: {self.project_dir}")

        # Load metadata
        data = self.load_metadata()
        print(f"✓ Loaded metadata for {data['metadata']['client_name']}")

        # Generate all sections
        print("\n=== Generating Proposal Sections ===")

        self.proposal_data['metadata'] = data['metadata']
        self.proposal_data['executive_summary'] = self.generate_executive_summary(data)
        self.proposal_data['your_business'] = self.generate_your_business(data)
        self.proposal_data['competitive_analysis'] = self.generate_competitive_analysis(data)
        self.proposal_data['strategy'] = self.generate_strategy(data)
        self.proposal_data['success_metrics'] = self.generate_success_metrics(data)
        self.proposal_data['timeline'] = self.generate_timeline(data)
        self.proposal_data['investment'] = self.generate_investment(data)
        self.proposal_data['next_steps'] = self.generate_next_steps(data)

        # Save intermediate JSON
        json_file = output_file.parent / (output_file.stem + '_data.json')
        with open(json_file, 'w') as f:
            json.dump(self.proposal_data, f, indent=2)
        print(f"\n💾 Saved intermediate data: {json_file}")

        # Assemble final HTML
        from assembler import ProposalAssembler
        assembler = ProposalAssembler(
            Path(__file__).parent / 'templates' / 'template.html',
            Path(__file__).parent / 'templates' / 'proposal.css'
        )

        final_html = assembler.assemble(self.proposal_data)

        with open(output_file, 'w') as f:
            f.write(final_html)

        print(f"\n✅ Proposal Generated: {output_file}")
        print(f"📊 Size: {len(final_html)} characters")


def main():
    if len(sys.argv) != 3:
        print("Usage: python proposal_generator.py <project_dir> <output_file>")
        print("Example: python proposal_generator.py ./client-project proposal.html")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).expanduser()
    output_file = Path(sys.argv[2])

    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    if not project_dir.exists():
        print(f"❌ Error: Project directory not found: {project_dir}")
        sys.exit(1)

    # Generate proposal
    generator = ProposalGenerator(project_dir, api_key)
    generator.generate(output_file)


if __name__ == '__main__':
    main()
