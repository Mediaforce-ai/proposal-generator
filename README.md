# Mediaforce Proposal Generator

AI-powered digital marketing proposal generator that creates BMW-style professional proposals.

**📋 [VERSION_SUMMARY.md](VERSION_SUMMARY.md)** - Quick reference card for v1.1 features, icons, and components

---

## 🌐 Web Application (Staff Self-Service)

The proposal generator is available as a web application for Mediaforce staff.

### Quick Start (Development)

```bash
# 1. Clone the repository
git clone https://github.com/Mediaforce-ai/proposal-generator.git
cd proposal-generator

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your settings

# 5. Run the app
export FLASK_ENV=development
python app.py
```

Open http://localhost:5000 in your browser.

### Production Deployment (Docker)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t proposal-generator .
docker run -p 5000:5000 --env-file .env proposal-generator
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes (prod) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes (prod) |
| `ALLOWED_DOMAINS` | Comma-separated allowed email domains | No (default: mediaforce.ca) |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI generation | Optional |
| `FLASK_ENV` | development or production | No |

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new OAuth 2.0 Client ID
3. Set authorized redirect URI to: `https://your-domain.com/authorize`
4. Copy Client ID and Secret to your `.env` file

### Deployment Options

- **Railway**: One-click deploy with Dockerfile
- **Vercel**: Use `vercel.json` configuration
- **AWS/GCP**: Use Docker image with ECS/Cloud Run
- **Self-hosted**: Use Docker Compose with Nginx reverse proxy

---

## 🚀 Quick Reference (CLI Usage)

**For New Proposals:**
```bash
# 1. Create project structure
cd ~/AI/TOOLS/mediaforce-proposal-generator
python3 init_project.py "Client Name"

# 2. Edit metadata.json with client details
# ~/AI/CLIENT_NAME/metadata.json

# 3. Copy generation scripts
cp examples/generate_sections_template.py ~/AI/CLIENT_NAME/generate_sections.py
cp examples/assemble_proposal.py ~/AI/CLIENT_NAME/assemble_proposal.py

# 4. Generate proposal
cd ~/AI/CLIENT_NAME
python3 generate_sections.py && python3 assemble_proposal.py && open Proposal.html
```

**Style Guidelines:** See `STYLE_GUIDE.md` for complete styling rules

## 📧 Workflow Overview

1. **Client fills out intake form** → Email received with client details
2. **Create project** → `init_project.py "Client Name"`
3. **Populate metadata.json** → Transfer form data to metadata.json (from email)
4. **Generate proposal** → `proposal_generator.py` creates BMW-style HTML
5. **Review & send** → Export to PDF or send HTML to client

### Email Form Integration

When clients submit the intake form via email, the form data should map to metadata.json fields:

| Form Field | metadata.json Field |
|-----------|-------------------|
| Company Name | `metadata.client_name` |
| Industry | `client_context.industry` |
| Brands/Products | `client_context.brands` |
| Location | `client_context.location` |
| Current Challenges | `client_context.current_situation.pain_points` |
| Goals (3-6 months) | `client_context.success_definition.short_term` |
| Goals (1-3 years) | `client_context.success_definition.long_term` |
| Target Audience | `client_context.target_audience.*` |
| Monthly Budget | `strategy.pillars.*.monthly_budget` |
| Competitors | `competitive_landscape.competitors` |

**Future Enhancement:** A script can be created to automatically parse email form submissions and generate metadata.json.

## 🎯 What It Does

Generates complete, professional digital marketing proposals with:
- Executive Summary
- Understanding Your Business & Challenges
- Competitive Analysis
- Our Approach & Strategy
- Success Metrics & ROI
- Implementation Timeline
- Investment/Pricing
- Next Steps

## 📋 Requirements

- Python 3.9+
- Anthropic API key
- `anthropic` Python package

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install anthropic
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Initialize Client Project

Use the helper script to create a new project:

```bash
cd ~/AI/TOOLS/mediaforce-proposal-generator
python3 init_project.py "Client Name"
```

This creates:
- `~/AI/CLIENT_NAME/` directory (client name in CAPS)
- `metadata.json` template pre-filled with client name and date

### 4. Customize `metadata.json`

Edit the generated metadata.json with client-specific details (from email form data):

```json
{
  "metadata": {
    "client_name": "Acme Corporation",
    "proposal_date": "2025-11-04",
    "analyst": "The Mediaforce Team",
    "proposal_type": "Digital Marketing Strategy Proposal"
  },
  "client_context": {
    "industry": "Technology",
    "brands": ["Acme Cloud", "Acme AI"],
    "location": "San Francisco Bay Area",
    "current_situation": {
      "description": "Growing SaaS company seeking to expand digital presence",
      "pain_points": [
        "Limited social media engagement",
        "Poor SEO rankings",
        "Low conversion rates from paid ads"
      ]
    },
    "success_definition": {
      "short_term": [
        "Increase website traffic by 50% in 3 months",
        "Improve lead quality and conversion rates"
      ],
      "long_term": [
        "Establish market leadership in target segments",
        "Build sustainable organic traffic growth"
      ]
    },
    "target_audience": {
      "demographics": ["B2B decision makers", "IT directors", "CTOs"],
      "psychographics": ["Innovation-focused", "Data-driven"],
      "behaviors": ["Active on LinkedIn", "Research before purchase"]
    }
  },
  "competitive_landscape": {
    "market_overview": "Highly competitive SaaS market with strong incumbents",
    "competitors": [
      {
        "name": "Competitor A",
        "strengths": ["Brand recognition", "Large marketing budget"],
        "weaknesses": ["Slow to adapt", "Poor customer service reputation"]
      }
    ],
    "opportunities": [
      "Underserved mid-market segment",
      "Growing demand for AI-powered solutions"
    ]
  },
  "strategy": {
    "pillars": {
      "google_ads": {
        "enabled": true,
        "monthly_budget": 10000,
        "campaigns": [
          {
            "name": "Branded Search",
            "budget": 3000,
            "description": "Protect brand terms and drive high-intent traffic"
          }
        ],
        "tactics": ["Dynamic keyword insertion", "Competitor targeting"],
        "expected_results": {
          "timeframe": "90 days",
          "metrics": ["500+ qualified leads", "15% conversion rate"]
        }
      },
      "seo": {
        "enabled": true,
        "focus_areas": ["Technical SEO", "Content marketing", "Link building"],
        "tactics": ["Blog content", "Industry partnerships"],
        "expected_results": {
          "timeframe": "3-6 months",
          "metrics": ["Top 5 rankings for 20 keywords", "300% organic traffic increase"]
        }
      },
      "paid_social": {
        "enabled": true,
        "monthly_budget": 8000,
        "platforms": ["LinkedIn", "Twitter"],
        "campaigns": ["Thought leadership", "Lead generation"],
        "tactics": ["Account-based marketing", "Retargeting"],
        "expected_results": {
          "timeframe": "90 days",
          "metrics": ["200+ MQLs", "$80 cost per lead"]
        }
      }
    },
    "creative_services": {
      "google_ads": ["Ad copy", "Landing pages"],
      "social_media": ["LinkedIn carousel ads", "Video content"],
      "landing_pages": ["Design", "A/B testing"]
    }
  },
  "success_metrics": {
    "primary_kpis": [
      "Website traffic",
      "Marketing Qualified Leads (MQLs)",
      "Cost per lead",
      "Conversion rate"
    ],
    "reporting": {
      "real_time_dashboard": true,
      "weekly_updates": true,
      "monthly_strategy_sessions": true,
      "quarterly_reviews": true
    },
    "projections": {
      "month_1_3": {
        "website_visits": "10,000-15,000 per month",
        "leads": "200-300 per month",
        "cost_per_lead": "$120-150"
      },
      "month_4_6": {
        "website_visits": "20,000-25,000 per month",
        "leads": "400-500 per month",
        "cost_per_lead": "$80-100"
      },
      "month_7_12": {
        "website_visits": "30,000-40,000 per month",
        "leads": "600-800 per month",
        "cost_per_lead": "$60-80"
      }
    },
    "roi_example": {
      "monthly_investment": 25000,
      "avg_deal_value": 50000,
      "closing_rate": 0.20,
      "monthly_revenue": 500000,
      "roi_multiple": "20.0x"
    }
  },
  "timeline": {
    "week_1": {
      "title": "Onboarding & Discovery",
      "deliverables": ["Kickoff meeting", "Account setup", "Strategy alignment"]
    },
    "week_2": {
      "title": "Strategy & Setup",
      "deliverables": ["Campaign strategy", "Tracking implementation", "Creative brief"]
    },
    "week_3": {
      "title": "Creative Development",
      "deliverables": ["Ad copy", "Landing pages", "Creative assets"]
    },
    "week_4": {
      "title": "Campaign Launch",
      "deliverables": ["Launch campaigns", "Monitor performance", "Initial optimizations"]
    },
    "weeks_5_12": {
      "title": "Optimization & Scaling",
      "deliverables": ["Continuous optimization", "A/B testing", "Scale winners"]
    }
  },
  "investment": {
    "packages": [
      {
        "name": "COMPLETE DIGITAL MARKETING PACKAGE",
        "description": "Full-service digital marketing management",
        "monthly_retainer": 12000,
        "ad_spend": 18000,
        "total_monthly": 30000,
        "includes": [
          "Strategy & Planning - Comprehensive marketing strategy and quarterly planning",
          "Campaign Management - Google Ads, LinkedIn Ads, and social media management",
          "Creative Services - Ad copy, landing pages, and visual content creation",
          "Analytics & Reporting - Real-time dashboard, weekly updates, monthly strategy sessions"
        ]
      }
    ],
    "payment_terms": {
      "retainer": "Monthly",
      "ad_spend": "Direct to platforms",
      "contract_length": "6 months minimum"
    }
  },
  "next_steps": {
    "process": [
      "Schedule 30-minute discovery call",
      "Review and sign service agreement",
      "Begin Week 1 onboarding"
    ],
    "contact": {
      "name": "Mediaforce Team",
      "email": "jbon@mediaforce.ca",
      "phone": "(647) 555-0123",
      "website": "mediaforce.ca"
    }
  }
}
```

### 5. Generate Proposal

**Option A: Using generate_sections.py template (Recommended)**

```bash
# Copy the template to your client directory
cp ~/AI/TOOLS/mediaforce-proposal-generator/examples/generate_sections_template.py ~/AI/CLIENT_NAME/generate_sections.py
cp ~/AI/TOOLS/mediaforce-proposal-generator/examples/assemble_proposal.py ~/AI/CLIENT_NAME/assemble_proposal.py

# Generate and assemble
cd ~/AI/CLIENT_NAME
python3 generate_sections.py
python3 assemble_proposal.py
```

**Option B: Using AI-powered generator (requires API key)**

```bash
cd ~/AI/TOOLS/mediaforce-proposal-generator
python3 proposal_generator.py ~/AI/CLIENT_NAME ~/AI/CLIENT_NAME/Proposal.html
```

**Note:** The template approach (Option A) is faster and doesn't require an API key. It uses pre-defined patterns that follow all style guidelines.

## 📁 Directory Structure

### Tool Location (~/AI/TOOLS/mediaforce-proposal-generator/)
```
mediaforce-proposal-generator/
├── proposal_generator.py           # AI-powered generator (requires API key)
├── assembler.py                   # HTML assembly engine
├── init_project.py                # Project initialization helper
├── README.md                      # Main documentation (you are here)
├── STYLE_GUIDE.md                 # Comprehensive styling guidelines ⭐
├── PREFERENCES.json               # Stored design preferences and defaults ⭐
├── CHANGES.md                     # Version history and change log ⭐
├── VERSION_SUMMARY.md             # Quick reference card (v1.1 features) ⭐
├── requirements.txt               # Python dependencies
├── templates/
│   ├── template.html              # BMW-style HTML template
│   └── proposal.css               # Mediaforce styling (11pt, contrast rules)
└── examples/
    ├── metadata_template.json     # Template for client metadata (v1.1)
    ├── generate_sections_template.py  # Section generator template (v1.1) ⭐
    └── assemble_proposal.py       # Proposal assembler script
```

### Client Projects (~/AI/)
```
AI/
├── CLIENT_A/                      # Client name in CAPS
│   ├── metadata.json              # Client-specific data (from email form)
│   ├── generate_sections.py      # Section generator (copied from template)
│   ├── assemble_proposal.py      # Assembler (copied from template)
│   ├── proposal_data.json         # Generated section data
│   └── Proposal.html              # Final generated proposal
├── CLIENT_B/
│   ├── metadata.json
│   ├── generate_sections.py
│   ├── assemble_proposal.py
│   └── Proposal.html
├── TOOLS/
│   └── mediaforce-proposal-generator/
└── ...
```

## 🎨 Output Features

- **BMW-Style Design**: Exact replication of professional BMW proposal format
- **Mediaforce Branding**: Uses official Mediaforce logo and colors (#0e5881, #ffcc33)
- **Simplified Color Scheme**: Light blue and light gray section backgrounds only (brand focus: blue + gold)
- **Responsive**: Works on desktop, tablet, and mobile
- **Interactive Navigation**: Smooth-scrolling navigation menu
- **Print-Ready**: Optimized for PDF export

## 🎛️ Preferences & Configuration

All design preferences and defaults are stored in **`PREFERENCES.json`** including:

- **Branding colors** - Primary blue (#0e5881), Gold accent (#ffcc33)
- **Color scheme** - 2 background colors only (light blue, light gray)
- **Typography** - Font sizes, families, line heights
- **Timeline structure** - 3-week accelerated launch
- **Section layouts** - Icons, card configurations, spacing rules
- **Official asset URLs** - Logos, images, footer graphics
- **Contact information** - Standard phone (613 265 2120), email, website
- **Component guidelines** - info-box, card, card-grid, price-box usage
- **Design principles** - Color philosophy, icon usage, responsive breakpoints

**Why PREFERENCES.json?**
- **Consistency** - All proposals follow same design standards
- **Easy updates** - Change preferences in one place
- **Quick reference** - Find all design decisions in one file
- **Version tracking** - Documents v1.0 → v1.1 evolution

View the file: `cat PREFERENCES.json | jq` (requires jq for pretty printing)

## ⚙️ Customization

### Style Guide

**IMPORTANT:** Review `STYLE_GUIDE.md` for comprehensive styling guidelines including:
- Color contrast rules (dark backgrounds → white text, light backgrounds → dark text)
- Official asset URLs (logos must use CDN URLs)
- Platform logo patterns
- Typography standards (11pt body text)
- Box component usage

### Adjust Generation Prompts

Edit `proposal_generator.py` and modify the prompts in each `generate_*` method to change AI output style.

### Modify Styling

Edit `templates/proposal.css` to adjust colors, fonts, spacing, etc.

**CRITICAL:** Always maintain color contrast rules:
- Dark backgrounds (#0e5881, #0a4563) → white text
- Light backgrounds → dark text (#333)
- See `STYLE_GUIDE.md` for complete rules

### Change Template Structure

Edit `templates/template.html` to add/remove sections or modify layout.

## 🔧 Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"
```bash
export ANTHROPIC_API_KEY="your-key"
```

### "metadata.json not found"
Ensure `metadata.json` is in the project directory you're pointing to.

### Generation takes a long time
The AI generates 8 sections sequentially. Typical generation time: 2-5 minutes.

## 📝 Notes

- All AI-generated content is reviewed by Claude Sonnet 4.5
- Proposals follow Mediaforce's professional standards
- Output includes embedded CSS (single-file HTML)
- **Official Asset URLs:**
  - Mediaforce Logo: https://mediaforce.ca/wp-content/uploads/2025/10/mf-logo2.png
  - Google Ads Logo: https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png
  - Target Audience Image: https://mediaforce.ca/wp-content/uploads/2025/11/target-audience.png
- Platform logos automatically appear in relevant sections (e.g., Google Ads logo in "Our Approach")
- Target audience displayed in **three horizontal cards** with icons (👥 Demographics, 🎯 Psychographics & Behaviors, 🔍 Search Behavior)
- Vision for Success in **two side-by-side cards** (🎯 Short-Term Goals, 🚀 Long-Term Vision)
- Creative Services section with icons (🎨 Google Ads Creative, 📄 Landing Pages, 📊 Ongoing Optimization)
- **Investment Overview** - Google Ads logo (150px) in white rounded box at top of pricing section for branding
- **Footer Logos** - Partner platform logos at bottom of proposal for credibility and expertise showcase
- **Streamlined contact section** - centered, inline design with icons (📧 📞 🌐) uses 70% less vertical space
- Price references use "Monthly Service" language for professional tone
- Accelerated 3-week timeline with campaign launch in week 3
- Winter icon (❄️) in Peak Season Readiness section for seasonal urgency

## 🚀 Next Steps

1. Create your first proposal using the sample metadata
2. Customize the metadata.json for your actual client
3. Generate and review the output
4. Export to PDF or send HTML directly

## 📝 Recent Changes

### Version 1.2 - November 5, 2025

**Pricing standardization, AI-friendly SEO terminology, and enhanced transparency.**

**Key Updates:**
- 💰 **Pricing Defaults:** Google Ads $899/mo, SEO $1,100/mo, Ad Spend $1,500/mo
- 🤖 **AI-friendly SEO:** Required terminology for all SEO proposals
- 📊 **Management Fee Breakout:** Separate line items for transparency
- 🎨 **Header Logo:** Image logo (60px) replaces text
- 🚨 **Color Enforcement:** Light blue info-box only (no purple/custom gradients)

**See [CHANGES.md](CHANGES.md) for complete v1.2 details**

---

### Version 1.1 - November 4, 2025

**Major updates for faster launch, simplified branding, and improved visual hierarchy.**

**Documentation:**
- 📋 **[VERSION_SUMMARY.md](VERSION_SUMMARY.md)** - Quick reference card (icons, components, colors)
- 📖 **[CHANGES.md](CHANGES.md)** - Complete details and migration guide
- 📚 **[STYLE_GUIDE.md](STYLE_GUIDE.md)** - Comprehensive styling guidelines

### Quick Summary

**Timeline:** 3-week accelerated launch (campaign launch in Week 3)
**Colors:** Simplified to light blue (info-box) and light gray (cards) only
**Target Audience:** Three horizontal cards with icons (👥 🎯 🔍) - no image
**Vision for Success:** Two side-by-side cards (🎯 Short-Term, 🚀 Long-Term)
**Creative Services:** Icons added (🎨 📄 📊) for visual clarity
**Contact Section:** Streamlined inline design with icons (📧 📞 🌐) - 70% less space
**Seasonal Icons:** Added ❄️ for Peak Season Readiness sections
**Brand Focus:** Blue primary (#0e5881) + Gold accents (#ffcc33) exclusively

### Files Updated
- ✅ `generate_sections_template.py` - All changes applied
- ✅ `metadata_template.json` - 3-week timeline (v1.1)
- ✅ `proposal.css` - Target audience styling
- ✅ `STYLE_GUIDE.md` - Version history added
- ✅ `README.md` - This file
- ✅ `CHANGES.md` - Detailed change log (new)

## 📞 Support

For questions or issues, contact the Mediaforce team at jbon@mediaforce.ca
