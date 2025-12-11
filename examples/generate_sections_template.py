#!/usr/bin/env python3
"""
Mediaforce Proposal Generator - Section Generator Template
Last Updated: 2025-11-04

KEY FEATURES:
- 3-week accelerated timeline (launch in Week 3)
- Simplified color scheme: info-box (light blue) and cards (light gray) only
- Target audience: Three horizontal cards with icons (👥 🎯 🔍)
- Vision for Success: Two side-by-side cards (🎯 Short-Term, 🚀 Long-Term)
- Creative Services: Icons for visual clarity (🎨 📄 📊)
- Contact section: Streamlined inline design (📧 📞 🌐)
- Winter icon (❄️) for seasonal urgency
- Brand focus: Blue primary (#0e5881) + Gold accents (#ffcc33)

USAGE:
Copy this template to your client directory and customize with client-specific data.
All content is generated from metadata.json in the client directory.
"""

import json
from pathlib import Path

def load_metadata():
    with open('metadata.json', 'r') as f:
        return json.load(f)

def generate_executive_summary(data):
    """Generate executive summary section"""
    client = data['metadata']['client_name']
    budget = data['investment']['packages'][0]['total_monthly']
    roi_multiple = data['success_metrics']['roi_example']['roi_multiple']

    html = f"""
<div class="info-box">
    <p><strong>Challenge:</strong> {client} needs to maximize simulator bookings during peak winter season (December-April) and build a consistent, repeatable client base in the competitive Greater Montreal indoor golf market.</p>
</div>

<p>Golf 365 Quebec offers an exceptional indoor golf experience with high-tech simulators, food, drinks, and entertainment in Saint-Eustache. With peak season approaching, the critical challenge is ensuring full capacity utilization during December through April while building long-term customer retention.</p>

<p>Your current marketing channels—website, Facebook, and Instagram—provide a foundation, but capturing high-intent local traffic during your busiest months requires a laser-focused Google Ads strategy that dominates local search results.</p>

<div class="info-box">
    <h3>Our Recommendation: Peak Season Google Ads Domination</h3>
    <p>We recommend a focused <strong>${budget:,}/month Google Ads campaign</strong> specifically designed to:</p>
    <ul>
        <li><strong>Capture peak season demand</strong> with geo-targeted campaigns covering your 25-40 KM service radius (Laval, Montreal, St-Jerome, Blainville, Saint-Eustache)</li>
        <li><strong>Target high-intent searchers</strong> actively looking for "indoor golf" solutions in English and French</li>
        <li><strong>Compete aggressively</strong> against 6 established competitors in the Greater Montreal area</li>
        <li><strong>Drive bookings immediately</strong> with conversion-optimized ad copy and landing pages</li>
    </ul>
</div>

<div class="info-box">
    <h3>What Success Looks Like</h3>
    <div class="card-grid">
        <div class="card">
            <h4>High-Quality Traffic</h4>
            <p>Substantial qualified clicks from local golf enthusiasts actively searching for indoor golf options</p>
        </div>
        <div class="card">
            <h4>Consistent Inquiries</h4>
            <p>Strong flow of booking inquiries throughout peak season</p>
        </div>
        <div class="card">
            <h4>Efficient Investment</h4>
            <p>Cost-effective lead generation that maximizes your ad spend</p>
        </div>
        <div class="card">
            <h4>Maximum Capacity</h4>
            <p>Significantly increased simulator utilization during December-April</p>
        </div>
    </div>
</div>

<p><strong>Investment & ROI:</strong> With a ${budget:,}/month total investment, our Google Ads strategy is designed to deliver strong returns by driving consistent bookings during your peak season. Similar local service businesses we've worked with have seen significant revenue growth that far exceeds their marketing investment.</p>

<p>This proposal outlines a proven, data-driven approach to dominate your local market during peak season and build the sustainable, repeatable client base you need for long-term success.</p>
"""
    return html

def generate_your_business(data):
    """Generate understanding your business section"""
    client = data['metadata']['client_name']
    location = data['client_context']['location']
    industry = data['client_context']['industry']
    description = data['client_context']['current_situation']['description']
    pain_points = data['client_context']['current_situation']['pain_points']

    html = f"""
<h3>Your Business</h3>

<p><strong>{client}</strong> operates in the {industry} industry, providing a premium indoor golf experience at your Saint-Eustache location in the Greater Montreal Area. Your facility combines cutting-edge golf simulator technology with a social atmosphere that includes food, drinks, and entertainment—creating a unique destination for golf enthusiasts year-round.</p>

<div class="info-box">
    <p><strong>Location:</strong> {location}</p>
    <p><strong>Service Radius:</strong> 25-40 KM (Laval, Montreal, St-Jerome, Blainville, Saint-Eustache)</p>
    <p><strong>Peak Season:</strong> December through April (winter months)</p>
</div>

<p>{description}</p>

<h3>Current Challenges</h3>

<p>Through our discovery process, we've identified three critical challenges that require immediate attention:</p>

<div class="card-grid">
"""

    for i, pain_point in enumerate(pain_points, 1):
        html += f"""
    <div class="card">
        <h4>Challenge {i}</h4>
        <p>{pain_point}</p>
    </div>
"""

    html += """
</div>

<h3>Your Target Audience</h3>

<p>Your ideal customers are clearly defined:</p>

<div class="card-grid">
    <div class="card">
        <h4>👥 Demographics</h4>
        <ul>
"""

    for demo in data['client_context']['target_audience']['demographics']:
        html += f"            <li>{demo}</li>\n"

    html += """        </ul>
    </div>

    <div class="card">
        <h4>🎯 Psychographics & Behaviors</h4>
        <ul>
"""

    for psycho in data['client_context']['target_audience']['psychographics']:
        html += f"            <li>{psycho}</li>\n"

    html += """        </ul>
    </div>

    <div class="card">
        <h4>🔍 Search Behavior</h4>
        <ul>
"""

    for behavior in data['client_context']['target_audience']['behaviors']:
        html += f"            <li>{behavior}</li>\n"

    html += """        </ul>
    </div>
</div>

<h3>Your Vision for Success</h3>

<div class="card-grid">
    <div class="card">
        <h4>🎯 Short-Term Goals (3-6 months)</h4>
        <ul>
"""

    for goal in data['client_context']['success_definition']['short_term']:
        html += f"            <li>{goal}</li>\n"

    html += """        </ul>
    </div>

    <div class="card">
        <h4>🚀 Long-Term Vision (1-3 years)</h4>
        <ul>
"""

    for goal in data['client_context']['success_definition']['long_term']:
        html += f"            <li>{goal}</li>\n"

    html += """        </ul>
    </div>
</div>

<p style="margin-top: 20px;">Your goals are ambitious yet achievable with the right digital marketing strategy. The key is capturing high-intent local traffic precisely when potential customers are searching for indoor golf options during your peak season.</p>
"""

    return html

def generate_competitive_analysis(data):
    """Generate competitive analysis section"""
    market_overview = data['competitive_landscape']['market_overview']
    competitors = data['competitive_landscape']['competitors']
    opportunities = data['competitive_landscape']['opportunities']

    html = f"""
<h3>Market Landscape</h3>

<p>{market_overview}</p>

<div class="info-box">
    <p><strong>Competitive Intensity:</strong> The Greater Montreal indoor golf market includes {len(competitors)} established competitors, all competing for the same demographic during winter months. Success requires strategic positioning and aggressive local search domination.</p>
</div>

<h3>Competitive Analysis</h3>

<p>We've analyzed your primary competitors to identify opportunities for Golf 365 Quebec:</p>

<div class="card-grid">
"""

    for comp in competitors:
        html += f"""
    <div class="card">
        <h4>{comp['name']}</h4>
        <p><small><a href="{comp['url']}" target="_blank">{comp['url']}</a></small></p>
        <p><strong>Strengths:</strong></p>
        <ul>
"""
        for strength in comp['strengths']:
            html += f"            <li>{strength}</li>\n"

        html += """        </ul>
        <p><strong>Opportunities to Exploit:</strong></p>
        <ul>
"""
        for weakness in comp['weaknesses']:
            html += f"            <li>{weakness}</li>\n"

        html += """        </ul>
    </div>
"""

    html += """
</div>

<h3>Strategic Opportunities</h3>

<p>Based on our competitive analysis, we've identified key opportunities for Golf 365 Quebec to capture market share:</p>

<div class="info-box">
    <ul>
"""

    for opp in opportunities:
        html += f"        <li><strong>{opp}</strong></li>\n"

    html += """    </ul>
</div>

<p>The competitive landscape is challenging but far from saturated. With focused Google Ads campaigns targeting your specific geographic radius and emphasizing your unique value proposition (simulators + food + drinks + entertainment), Golf 365 Quebec can capture significant market share during peak season.</p>

<div class="info-box">
    <h4>Competitive Advantage</h4>
    <p>Golf 365 Quebec's combination of high-tech simulators, food and beverage service, and entertainment atmosphere creates a differentiated offering. Our Google Ads strategy will emphasize these unique elements to attract customers seeking more than just golf practice—they're looking for a complete social experience.</p>
</div>
"""

    return html

def generate_strategy(data):
    """Generate strategy and approach section"""
    google_ads = data['strategy']['pillars']['google_ads']
    campaigns = google_ads['campaigns']
    tactics = google_ads['tactics']
    expected = google_ads['expected_results']
    creative = data['strategy']['creative_services']

    # Official Google Ads logo URL - DO NOT CHANGE
    # https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png
    html = f"""
<h3>Our Strategic Approach</h3>

<div class="platform-logo-section">
    <div class="platform-badge">
        <img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png" alt="Google Ads" style="height: 40px; width: auto;">
        <span class="platform-badge-text">Powered by Google Ads</span>
    </div>
</div>

<p>Our recommendation is a focused Google Ads strategy designed specifically for peak season domination. This approach concentrates your investment where it delivers maximum ROI: capturing high-intent local searchers actively looking for indoor golf options.</p>

<div class="info-box">
    <h4>Why Google Ads First?</h4>
    <p>Google Ads delivers immediate results during your critical peak season (December-April). Unlike SEO or organic social media, which take 6-12 months to build momentum, Google Ads puts you at the top of search results the day campaigns launch—exactly when you need maximum bookings.</p>
</div>

<h3>Campaign Structure</h3>

<p>We'll deploy <strong>four targeted campaigns</strong> with a total monthly ad spend of <strong>${google_ads['monthly_budget']:,}</strong>:</p>

<div class="card-grid">
"""

    for camp in campaigns:
        html += f"""
    <div class="card">
        <h4>{camp['name']}</h4>
        <p><strong>Budget:</strong> ${camp['budget']}/month</p>
        <p>{camp['description']}</p>
    </div>
"""

    html += """
</div>

<h3>Tactical Execution</h3>

<p>Each campaign will leverage proven Google Ads tactics to maximize performance:</p>

<div class="info-box">
    <ul>
"""

    for tactic in tactics:
        html += f"        <li>{tactic}</li>\n"

    html += """    </ul>
</div>

<h3>Creative Services</h3>

<p>High-converting campaigns require exceptional creative execution. Our team will deliver:</p>

<div class="card-grid">
    <div class="card">
        <h4>🎨 Google Ads Creative</h4>
        <ul>
"""

    for item in creative['google_ads']:
        html += f"            <li>{item}</li>\n"

    html += """        </ul>
    </div>
    <div class="card">
        <h4>📄 Landing Pages</h4>
        <ul>
"""

    for item in creative['landing_pages']:
        html += f"            <li>{item}</li>\n"

    html += """        </ul>
    </div>
    <div class="card">
        <h4>📊 Ongoing Optimization</h4>
        <ul>
            <li>A/B testing ad variations</li>
            <li>Keyword performance analysis</li>
            <li>Bid strategy optimization</li>
            <li>Landing page conversion testing</li>
        </ul>
    </div>
</div>

<h3>Campaign Performance Goals</h3>

<div class="info-box">
    <h4>Our Focus During Peak Season</h4>
    <ul>
        <li>Drive substantial qualified traffic from your target geographic radius</li>
        <li>Generate consistent booking inquiries throughout December-April</li>
        <li>Maintain cost-efficient lead generation throughout the campaign</li>
        <li>Maximize simulator capacity utilization during peak months</li>
        <li>Build a foundation of repeat customers for long-term growth</li>
    </ul>
</div>

<p>Our approach is based on proven strategies used successfully with similar local service businesses in competitive markets. The key to success is aggressive campaign management, continuous optimization, and unwavering focus on your peak season booking goals.</p>

<div class="info-box">
    <h4>Why We're Confident</h4>
    <p>Your target audience is actively searching for indoor golf options on Google. They're high-intent customers ready to book. Our job is to ensure Golf 365 Quebec appears at the top of their search results with compelling messaging that drives immediate action.</p>
</div>
"""

    return html

def generate_success_metrics(data):
    """Generate success metrics and ROI section"""
    kpis = data['success_metrics']['primary_kpis']
    reporting = data['success_metrics']['reporting']
    projections = data['success_metrics']['projections']
    roi_example = data['success_metrics']['roi_example']

    html = """
<h3>Measuring Success</h3>

<p>We believe in complete transparency and data-driven decision making. Your success is measured by bookings, revenue, and ROI—not vanity metrics like impressions or clicks.</p>

<h3>Primary KPIs</h3>

<div class="card-grid">
"""

    for kpi in kpis:
        html += f"""
    <div class="card">
        <h4>{kpi}</h4>
        <p>Tracked daily and reported weekly</p>
    </div>
"""

    html += """
</div>

<h3>Reporting & Communication</h3>

<p>You'll have complete visibility into campaign performance:</p>

<div class="info-box">
    <ul>
"""

    if reporting['real_time_dashboard']:
        html += "        <li><strong>Real-Time Dashboard Access:</strong> View performance anytime via Google Ads dashboard</li>\n"
    if reporting['weekly_updates']:
        html += "        <li><strong>Weekly Performance Updates:</strong> Email summaries of key metrics and optimizations</li>\n"
    if reporting['monthly_strategy_sessions']:
        html += "        <li><strong>Monthly Strategy Calls:</strong> Review results, discuss optimizations, plan ahead</li>\n"

    html += """    </ul>
</div>

<h3>Performance Growth Trajectory</h3>

<p>Based on similar campaigns we've managed, here's the typical progression you can expect:</p>

<div class="card-grid">
    <div class="card">
        <h4>Early Phase (Months 1-3)</h4>
        <ul>
            <li><strong>Campaign Launch:</strong> Initial traffic and inquiry generation begins</li>
            <li><strong>Data Gathering:</strong> Learning which keywords and audiences convert best</li>
            <li><strong>Optimization:</strong> Continuous refinement of targeting and messaging</li>
            <li><strong>Goal:</strong> Establish consistent lead flow and booking patterns</li>
        </ul>
    </div>
    <div class="card">
        <h4>Growth Phase (Months 4-6)</h4>
        <ul>
            <li><strong>Scaling Winners:</strong> Increase investment in top-performing campaigns</li>
            <li><strong>Expanded Reach:</strong> Broaden targeting based on early insights</li>
            <li><strong>Cost Efficiency:</strong> Improved cost per booking as campaigns mature</li>
            <li><strong>Goal:</strong> Increase booking volume and peak season capacity</li>
        </ul>
    </div>
    <div class="card">
        <h4>Maturity Phase (Months 7-12)</h4>
        <ul>
            <li><strong>Peak Performance:</strong> Campaigns fully optimized and delivering consistently</li>
            <li><strong>Repeat Business:</strong> Previous customers returning for additional sessions</li>
            <li><strong>Brand Recognition:</strong> Growing awareness in your target market</li>
            <li><strong>Goal:</strong> Sustained high capacity utilization and customer retention</li>
        </ul>
    </div>
</div>

<h3>Understanding Return on Investment</h3>

<div class="price-box">
    <h4>How ROI Works for Your Business</h4>
    <p>A strategic marketing investment focused on driving measurable results. When you invest in targeted Google Ads campaigns, you're putting your business directly in front of customers actively searching for your services. Here's how it works:</p>

    <div class="card-grid">
        <div class="card">
            <h4>The Investment</h4>
            <p><strong>Monthly Service</strong></p>
            <p>Full-service Google Ads management with dedicated ad spend</p>
        </div>
        <div class="card">
            <h4>The Mechanism</h4>
            <p><strong>Targeted Traffic</strong></p>
            <p>High-intent local customers actively searching for indoor golf</p>
        </div>
        <div class="card">
            <h4>The Outcome</h4>
            <p><strong>Increased Bookings</strong></p>
            <p>More simulator reservations during peak season</p>
        </div>
        <div class="card">
            <h4>The Result</h4>
            <p><strong>Strong ROI</strong></p>
            <p>Revenue significantly exceeding marketing investment</p>
        </div>
    </div>
</div>

<div class="info-box">
    <h4>What Drives Success</h4>
    <p>Strong campaign performance typically results from:</p>
    <ul>
        <li><strong>Strategic Targeting:</strong> Focusing on high-intent local searches within your service radius</li>
        <li><strong>Competitive Positioning:</strong> Capturing market share from established competitors</li>
        <li><strong>Peak Season Timing:</strong> Maximizing visibility when demand is highest (December-April)</li>
        <li><strong>Compelling Messaging:</strong> Emphasizing your unique value proposition (simulators + food + drinks + entertainment)</li>
        <li><strong>Continuous Optimization:</strong> Daily monitoring and adjustments to improve performance</li>
    </ul>
    <p>Our focus is on driving bookings that generate revenue well above your marketing investment, creating sustainable growth for your business.</p>
</div>

<h3>Long-Term Value</h3>

<p>The true value extends beyond immediate bookings:</p>

<div class="info-box">
    <ul>
        <li><strong>Customer Lifetime Value:</strong> First-time customers who have a great experience become repeat customers, multiplying ROI over time</li>
        <li><strong>Word-of-Mouth:</strong> Satisfied customers recommend Golf 365 to friends and colleagues</li>
        <li><strong>Brand Building:</strong> Consistent visibility during peak season establishes Golf 365 as the regional leader</li>
        <li><strong>Data & Insights:</strong> Campaign data reveals what messaging, offers, and targeting work best for future seasons</li>
    </ul>
</div>
"""

    return html

def generate_timeline(data):
    """Generate implementation timeline"""
    timeline = data['timeline']

    html = """
<h3>Implementation Roadmap</h3>

<p>We follow an accelerated 3-week onboarding process to ensure campaigns launch successfully and deliver results immediately. Here's exactly what happens from contract signing to peak season domination:</p>

<div class="card-grid">
"""

    for week_key in ['week_1', 'week_2', 'week_3']:
        week = timeline[week_key]
        week_num = week_key.replace('_', ' ').title()
        html += f"""
    <div class="card">
        <h4>{week_num}</h4>
        <p><strong>{week['title']}</strong></p>
        <ul>
"""
        for deliverable in week['deliverables']:
            html += f"            <li>{deliverable}</li>\n"

        html += """        </ul>
    </div>
"""

    # Handle weeks 4-12
    if 'weeks_4_12' in timeline:
        week = timeline['weeks_4_12']
        html += f"""
    <div class="card" style="grid-column: span 2;">
        <h4>Weeks 4-12 (Ongoing)</h4>
        <p><strong>{week['title']}</strong></p>
        <ul>
"""
        for deliverable in week['deliverables']:
            html += f"            <li>{deliverable}</li>\n"

        html += """        </ul>
    </div>
"""

    html += """
</div>

<div class="info-box">
    <h4>Why This Timeline Works</h4>
    <p>The 3-week accelerated timeline ensures campaigns launch quickly without sacrificing strategic quality. Our streamlined process gets your campaigns live faster, so you can start capturing peak season bookings immediately while maintaining proper tracking and creative excellence.</p>
</div>

<div class="info-box">
    <h4>❄️ Peak Season Readiness</h4>
    <p>If we begin onboarding now, campaigns will be fully optimized and delivering maximum results well before your peak season intensifies in December. Early launch also provides valuable data to refine targeting and messaging before your busiest months.</p>
</div>

<h3>What We Need From You</h3>

<p>To ensure a smooth onboarding process, we'll need:</p>

<div class="info-box">
    <ul>
        <li><strong>Week 1:</strong> Google Ads account access (or we'll create one), website access for tracking implementation, high-quality photos of your facility</li>
        <li><strong>Week 2:</strong> Feedback on initial campaign strategy and keyword selections, review ad copy and landing page recommendations</li>
        <li><strong>Week 3:</strong> Final approval to launch campaigns</li>
    </ul>
</div>

<p>Our team handles all technical implementation, creative development, and campaign management. Your role is strategic oversight and approval at key milestones.</p>
"""

    return html

def generate_investment(data):
    """Generate investment/pricing section"""
    packages = data['investment']['packages']
    payment_terms = data['investment']['payment_terms']

    html = """
<h3>Investment Overview</h3>

<p>Our pricing is transparent, straightforward, and designed to deliver exceptional ROI. There are no hidden fees, no surprise charges, and no long-term contracts locking you in.</p>
"""

    for package in packages:
        intro_retainer = package.get('monthly_retainer', 750)
        regular_retainer = package.get('monthly_retainer_after_intro', 950)
        intro_months = package.get('intro_period_months', 3)
        ad_spend = package.get('ad_spend', 1500)
        intro_total = intro_retainer + ad_spend
        regular_total = regular_retainer + ad_spend

        html += f"""
<div class="price-box">
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="background: white; border-radius: 12px; padding: 20px; display: inline-block;">
            <img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png" alt="Google Ads" style="width: 150px; height: auto;">
        </div>
    </div>
    <h4>{package['name']}</h4>
    <p>{package['description']}</p>

    <div class="info-box" style="background: rgba(255,255,255,0.15); border: none; margin: 20px 0;">
        <h4 style="color: #ffcc33; margin-top: 0;">⭐ Introductory Offer - First {intro_months} Months</h4>
        <p style="font-size: 13pt;"><strong>${intro_total:,}/month total</strong> (${intro_retainer}/month management + ${ad_spend:,}/month ad spend)</p>
    </div>

    <div class="card-grid">
        <div class="card">
            <h4>Management Fee</h4>
            <p><strong>Months 1-{intro_months}: ${intro_retainer}/month</strong></p>
            <p>After month {intro_months}: ${regular_retainer}/month</p>
            <p style="font-size: 9pt; color: #666;">Paid to Mediaforce</p>
        </div>
        <div class="card">
            <h4>Ad Spend</h4>
            <p><strong>${ad_spend:,}/month</strong></p>
            <p style="font-size: 9pt; color: #666;">Consistent throughout</p>
            <p style="font-size: 9pt; color: #666;">Paid directly to Google</p>
        </div>
        <div class="card">
            <h4>Total Investment</h4>
            <p><strong>Months 1-{intro_months}: ${intro_total:,}/month</strong></p>
            <p>After month {intro_months}: ${regular_total:,}/month</p>
            <p style="font-size: 9pt; color: #666;">All-inclusive</p>
        </div>
    </div>

    <h4>What's Included</h4>
    <ul>
"""

        for item in package['includes']:
            html += f"        <li>{item}</li>\n"

        html += """    </ul>
</div>
"""

    html += f"""
<h3>Payment Terms</h3>

<div class="info-box">
    <ul>
        <li><strong>Management Retainer:</strong> {payment_terms['retainer']}</li>
        <li><strong>Ad Spend:</strong> {payment_terms['ad_spend']}</li>
        <li><strong>Contract Length:</strong> {payment_terms['contract_length']}</li>
        <li><strong>Billing:</strong> {payment_terms['billing']}</li>
    </ul>
</div>

<h3>Why This Investment Makes Sense</h3>

<div class="info-box">
    <p><strong>Proven ROI Potential:</strong> With a ${packages[0]['total_monthly']:,}/month total investment, a strong Google Ads campaign can generate significant booking volume. When you consider typical group bookings and your peak season demand, the revenue potential substantially exceeds the marketing investment.</p>

    <p><strong>Scalability:</strong> As campaigns optimize and booking volume increases, we can scale ad spend to capture additional demand without increasing management fees proportionally.</p>

    <p><strong>No Long-Term Lock-In:</strong> The {payment_terms['contract_length']} allows you to evaluate results during peak season. If we don't deliver, you're not stuck in a lengthy contract.</p>
</div>

<h3>Comparing Options</h3>

<p>Consider the alternatives:</p>

<div class="card-grid">
    <div class="card">
        <h4>Hiring In-House</h4>
        <p>Digital marketing manager salary: $60,000-80,000/year plus benefits, training, and Google Ads expertise gaps</p>
    </div>
    <div class="card">
        <h4>Large Agency</h4>
        <p>Typical pricing: $3,000-5,000/month management fees with 6-12 month contracts and junior account managers</p>
    </div>
    <div class="card">
        <h4>Mediaforce</h4>
        <p>${packages[0]['monthly_retainer']}/month management with direct access to experienced strategists and flexible contract terms</p>
    </div>
</div>

<div class="info-box">
    <h4>Our Commitment</h4>
    <p>We succeed when you succeed. Our pricing reflects a partnership approach—we're focused on delivering bookings and revenue, not maximizing billable hours. If campaigns aren't performing, we optimize aggressively or recommend changes, even if it means reducing our own fees.</p>
</div>
"""

    return html

def generate_next_steps(data):
    """Generate next steps section"""
    next_steps = data['next_steps']
    contact = next_steps['contact']

    html = f"""
<h3>Ready to Dominate Peak Season?</h3>

<p>The window to capture maximum bookings during December-April is closing. Competitors are already ramping up their marketing. The longer you wait, the more market share you concede to established players.</p>

<div class="info-box">
    <h4>Time-Sensitive Opportunity</h4>
    <p>Peak season is just weeks away. Starting now ensures your Google Ads campaigns are fully optimized and delivering maximum results before the December rush. Waiting until mid-December means missing the critical early booking wave.</p>
</div>

<h3>Your Next Steps</h3>

<p>Getting started is simple and fast:</p>

<div class="card-grid">
"""

    for i, step in enumerate(next_steps['process'], 1):
        html += f"""
    <div class="card">
        <h4>Step {i}</h4>
        <p>{step}</p>
    </div>
"""

    html += f"""
</div>

<div class="info-box">
    <h4>Our Promise</h4>
    <p>Within 30 days of signing, your Google Ads campaigns will be live and driving qualified traffic to Golf 365 Quebec. Within 90 days, you'll see measurable increases in bookings and capacity utilization. And by the end of peak season, you'll have the data and client base to make this your most successful winter ever.</p>
</div>

<h3>Let's Talk</h3>

<div class="info-box" style="text-align: center; padding: 25px;">
    <p style="margin-bottom: 15px;">Ready to discuss your peak season strategy? Let's connect.</p>
    <p style="font-size: 13pt; margin: 10px 0;">
        <strong>📧</strong> <a href="mailto:{contact['email']}" style="color: #0e5881; text-decoration: none;">{contact['email']}</a>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <strong>📞</strong> {contact['phone']}
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <strong>🌐</strong> <a href="https://{contact['website']}" target="_blank" style="color: #0e5881; text-decoration: none;">{contact['website']}</a>
    </p>
</div>

<h3>Why Choose Mediaforce?</h3>

<p>We're not a typical agency churning through clients with cookie-cutter strategies. Mediaforce specializes in local service businesses like Golf 365 Quebec—companies that need immediate results, transparent communication, and partners who understand the urgency of peak season.</p>

<div class="info-box">
    <ul>
        <li><strong>Local Expertise:</strong> We understand the Greater Montreal market and competitive dynamics</li>
        <li><strong>Google Ads Specialists:</strong> We live and breathe Google Ads performance optimization</li>
        <li><strong>Booking-Focused:</strong> We measure success by bookings and revenue, not vanity metrics</li>
        <li><strong>Transparent Reporting:</strong> You'll always know exactly where your budget is going and what results you're getting</li>
        <li><strong>Peak Season Urgency:</strong> We understand the time-sensitive nature of your business and move fast</li>
    </ul>
</div>

<p>Thank you for considering Mediaforce as your digital marketing partner. We're excited about the opportunity to help Golf 365 Quebec dominate peak season and build a thriving, sustainable client base.</p>

<p><strong>Let's make this your best winter season ever.</strong></p>

<div class="info-box">
    <p style="text-align: center; font-size: 12pt;"><strong>Contact us today: {contact['email']} | {contact['phone']}</strong></p>
</div>

<div style="text-align: center; margin: 40px 0 20px 0;">
    <img src="https://mediaforce.ca/wp-content/uploads/2025/11/footer-logos.png" alt="Partner Platforms" style="max-width: 100%; height: auto;">
</div>
"""

    return html

def main():
    print("Loading metadata...")
    data = load_metadata()

    print("Generating proposal sections...")

    sections = {
        'executive_summary': generate_executive_summary(data),
        'your_business': generate_your_business(data),
        'competitive_analysis': generate_competitive_analysis(data),
        'strategy': generate_strategy(data),
        'success_metrics': generate_success_metrics(data),
        'timeline': generate_timeline(data),
        'investment': generate_investment(data),
        'next_steps': generate_next_steps(data)
    }

    # Save sections as JSON
    output_data = {
        'metadata': data['metadata'],
        **sections
    }

    with open('proposal_data.json', 'w') as f:
        json.dump(output_data, f, indent=2)

    print("✅ All sections generated successfully!")
    print("📁 Saved to: proposal_data.json")
    print("\nNext: Run assembler to create final HTML")

if __name__ == '__main__':
    main()
