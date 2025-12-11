# Mediaforce Proposal Generator - Style Guide

## Typography

### Body Text
- **Font Family:** 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- **Font Size:** 11pt
- **Line Height:** 1.6
- **Color:** #333 (dark gray) on light backgrounds, white on dark backgrounds

### Headings
- **H1:** 32pt, white on dark blue cover section
- **H2:** 18pt
- **H3:** 16pt
- **H4:** 13pt

## Color Palette

### Primary Colors
- **Mediaforce Blue:** #0e5881
- **Dark Blue:** #0a4563
- **Gold Accent:** #ffcc33
- **Dark Gray:** #333

### Background Colors
- **White:** #ffffff
- **Light Gray:** #f9f9f9, #f5f5f5
- **Light Blue (Info):** #e8f4f8
- **Light Green (Success):** #E8F5E9
- **Light Orange (Warning):** #FFF3E0
- **Light Yellow (Highlight):** #FFF8E1

## Color Contrast Rules

### **CRITICAL: Dark Backgrounds → White Text**

All sections with dark blue backgrounds (#0e5881, #0a4563) must have white text:

```css
/* Cover Section */
.cover { background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%); color: white; }
.cover h1 { color: white; }
.cover h2 { color: white; }
.meta-item strong { color: white; }
.meta-item span { color: white; }

/* Price Box */
.price-box { background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%); color: white; }
.price-box h3 { color: white; }
.price-box h4 { color: white; }
.price-box p { color: white; }
.price-box ul { color: white; }
.price-box li { color: white; }
.price-box strong { color: white; }

/* Navigation Menu */
.nav-menu { background: linear-gradient(135deg, #0e5881 0%, #0a4563 100%); }
.nav-menu-link { color: white; }
```

### **CRITICAL: Light Backgrounds → Dark Text**

All sections with light backgrounds must have dark text (#333):

```css
/* Info Boxes */
.info-box { background: #e8f4f8; } /* inherits body color: #333 */
.success-box { background: #E8F5E9; } /* inherits body color: #333 */
.warning-box { background: #FFF3E0; } /* inherits body color: #333 */
.highlight-box { background: #FFF8E1; } /* inherits body color: #333 */

/* Cards */
.card { background: #f9f9f9; } /* inherits body color: #333 */

/* Special Case: Cards Inside Dark Price-Box */
.price-box .card { color: #333; }
.price-box .card h4 { color: #0e5881; }
.price-box .card p { color: #333; }
.price-box .card strong { color: #333; }
```

## Platform Logos

### Official Asset URLs

**ALWAYS USE THESE EXACT URLs:**

- **Mediaforce Logo:** `https://mediaforce.ca/wp-content/uploads/2025/10/mf-logo2.png`
- **Google Ads Logo:** `https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png`
- **Target Audience Image:** `https://mediaforce.ca/wp-content/uploads/2025/11/target-audience.png`

### Platform Badge Usage

When featuring a platform (e.g., Google Ads), use the platform badge component:

```html
<div class="platform-logo-section">
    <div class="platform-badge">
        <img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png"
             alt="Google Ads"
             style="height: 40px; width: auto;">
        <span class="platform-badge-text">Powered by Google Ads</span>
    </div>
</div>
```

**CSS Classes:**
- `.platform-logo-section` - Container with light gray background (#f9f9f9)
- `.platform-badge` - White badge with shadow and hover effects
- `.platform-badge img` - Logo image (40px height)
- `.platform-badge-text` - Badge text (11pt, bold, #333)

### When to Use Platform Logos

- **Google Ads:** Display in "Our Approach" or "Strategy" section when Google Ads campaigns are enabled
- **Facebook/Instagram:** Display when paid social campaigns are enabled
- **LinkedIn:** Display when B2B social campaigns are enabled
- **Other Platforms:** Follow the same pattern for any additional platforms

### Target Audience Section

Display target audience information in **three horizontal cards** with icons:

```html
<div class="card-grid">
    <div class="card">
        <h4>👥 Demographics</h4>
        <ul>
            <li>Demographic info...</li>
        </ul>
    </div>

    <div class="card">
        <h4>🎯 Psychographics & Behaviors</h4>
        <ul>
            <li>Psychographic info...</li>
        </ul>
    </div>

    <div class="card">
        <h4>🔍 Search Behavior</h4>
        <ul>
            <li>Behavior info...</li>
        </ul>
    </div>
</div>
```

**Layout:**
- **Three horizontal cards** using card-grid layout
- **Icons:** 👥 (Demographics), 🎯 (Psychographics & Behaviors), 🔍 (Search Behavior)
- **Responsive:** Auto-fits columns on desktop, stacks vertically on mobile

**Styling:**
- Uses standard card styling (light gray background, gold left border)
- 20px gap between cards
- Responsive grid: minmax(280px, 1fr)

**Icons:**
- 👥 Demographics - Represents people/audience
- 🎯 Psychographics & Behaviors - Represents targeting
- 🔍 Search Behavior - Represents research/searching

### Creative Services Section

Display creative services in **three horizontal cards** with relevant icons:

```html
<div class="card-grid">
    <div class="card">
        <h4>🎨 Google Ads Creative</h4>
        <ul>
            <li>Service item...</li>
        </ul>
    </div>
    <div class="card">
        <h4>📄 Landing Pages</h4>
        <ul>
            <li>Service item...</li>
        </ul>
    </div>
    <div class="card">
        <h4>📊 Ongoing Optimization</h4>
        <ul>
            <li>Service item...</li>
        </ul>
    </div>
</div>
```

**Icons:**
- 🎨 Google Ads Creative - Represents design/creativity
- 📄 Landing Pages - Represents web pages/content
- 📊 Ongoing Optimization - Represents data analysis/performance

### Vision for Success Section

Display short-term and long-term goals in **two side-by-side cards**:

```html
<h3>Your Vision for Success</h3>

<div class="card-grid">
    <div class="card">
        <h4>🎯 Short-Term Goals (3-6 months)</h4>
        <ul>
            <li>Goal 1...</li>
            <li>Goal 2...</li>
        </ul>
    </div>

    <div class="card">
        <h4>🚀 Long-Term Vision (1-3 years)</h4>
        <ul>
            <li>Vision 1...</li>
            <li>Vision 2...</li>
        </ul>
    </div>
</div>

<p style="margin-top: 20px;">Your goals are ambitious yet achievable...</p>
```

**Layout:**
- **Two-column card layout** on desktop
- **Stacks vertically** on mobile (< 768px)
- **Icons:** 🎯 (Short-term, targeting), 🚀 (Long-term, growth)

**Benefits:**
- Easy visual comparison of short vs. long-term goals
- Better use of horizontal space
- Consistent with card-based design system

### Investment Overview Section

Display Google Ads logo at the top of the price-box for visual branding:

```html
<div class="price-box">
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="background: white; border-radius: 12px; padding: 20px; display: inline-block;">
            <img src="https://mediaforce.ca/wp-content/uploads/2025/11/guide-google-ads.png"
                 alt="Google Ads"
                 style="width: 150px; height: auto;">
        </div>
    </div>
    <h4>GOOGLE ADS MANAGEMENT - FOCUSED BOOKING STRATEGY</h4>
    <p>Description...</p>
    ...
</div>
```

**Styling:**
- **White rounded box** background (border-radius: 12px, padding: 20px)
- **Centered** at top of price-box with inline-block display
- **Width:** 150px (height auto-scales)
- **Margin:** 20px bottom on outer container
- **Contrast:** White box stands out against dark blue price-box background

**Purpose:**
- Reinforces Google Ads focus of the package
- Professional branding
- Visual identification of platform

### Contact Section (Let's Talk)

Streamlined, centered contact information in a single info-box:

```html
<h3>Let's Talk</h3>

<div class="info-box" style="text-align: center; padding: 25px;">
    <p style="margin-bottom: 15px;">Ready to discuss your peak season strategy? Let's connect.</p>
    <p style="font-size: 13pt; margin: 10px 0;">
        <strong>📧</strong> <a href="mailto:email@example.com" style="color: #0e5881; text-decoration: none;">email@example.com</a>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <strong>📞</strong> (123) 456-7890
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <strong>🌐</strong> <a href="https://website.com" target="_blank" style="color: #0e5881; text-decoration: none;">website.com</a>
    </p>
</div>
```

**Design Features:**
- **Centered layout** for visual emphasis
- **Inline contact info** with icon separators (📧 📞 🌐)
- **Compact format** - takes minimal vertical space
- **Blue link colors** matching brand (#0e5881)
- **Clean styling** with no underlines on links

**Benefits:**
- 70% less vertical space than card-grid layout
- Easier to scan all contact methods at once
- Professional, modern appearance
- Mobile-friendly single line (wraps gracefully)

### Footer Logos Section

Display partner platform logos at the bottom of the proposal (above footer):

```html
<div style="text-align: center; margin: 40px 0 20px 0;">
    <img src="https://mediaforce.ca/wp-content/uploads/2025/11/footer-logos.png"
         alt="Partner Platforms"
         style="max-width: 100%; height: auto;">
</div>
```

**Styling:**
- **Centered** for visual balance
- **Responsive width** (max-width: 100%) adapts to screen size
- **Margins:** 40px top, 20px bottom for proper spacing
- **Placement:** At end of Next Steps section, just before final return statement

**Purpose:**
- Showcases platform partnerships (Google, Meta, LinkedIn, etc.)
- Reinforces multi-platform expertise
- Professional credibility and trust building
- Visual closure before footer

**Image Content:**
- Should include logos of all platforms offered (Google Ads, Meta, LinkedIn, etc.)
- Transparent or white background works best
- Horizontal layout for footer positioning

## Timeline Structure

### Standard Timeline: 3-Week Accelerated Launch

The default timeline structure is a 3-week accelerated process with campaign launch in week 3:

```json
"timeline": {
  "week_1": {
    "title": "Onboarding & Discovery",
    "deliverables": [...]
  },
  "week_2": {
    "title": "Campaign Strategy & Build",
    "deliverables": [...]
  },
  "week_3": {
    "title": "Final QA & Campaign Launch",
    "deliverables": [...]
  },
  "weeks_4_12": {
    "title": "Optimization & Scaling",
    "deliverables": [...]
  }
}
```

**Why 3 Weeks:**
- Faster time-to-market for seasonal campaigns
- Maintains strategic quality without delay
- Ideal for peak season urgency (e.g., December winter sports)

### Peak Season Readiness Section

For seasonal businesses, include a winter icon (❄️) in the Peak Season Readiness section:

```html
<div class="success-box">
    <h4>❄️ Peak Season Readiness</h4>
    <p>If we begin onboarding now, campaigns will be fully optimized and delivering maximum results well before your peak season intensifies in December...</p>
</div>
```

**When to Use:**
- Winter sports businesses (golf, skiing, etc.)
- Holiday-focused campaigns
- Any seasonal business with urgency

**Alternative Icons:**
- 🏖️ for summer season
- 🎃 for fall/Halloween campaigns
- 🎄 for Christmas campaigns

## Box Components

### Simplified Color Scheme

**Brand Focus:** Blue primary color with gold accents only. All section backgrounds use light blue or light gray.

### Info Box (Light Blue) - Primary Section Container
```html
<div class="info-box">
    <h4>Title</h4>
    <p>Content with dark text...</p>
</div>
```
**Background:** #e8f4f8 (light blue)
**Border:** 4px solid #0e5881 (left side, Mediaforce blue)
**Text Color:** #333 (dark gray)

**Usage:** Use for all highlighted sections, key information, recommendations, and important callouts

### Price Box (Dark Blue)
```html
<div class="price-box">
    <h4>Title</h4>
    <p>Content with WHITE text...</p>

    <div class="card-grid">
        <div class="card">
            <h4>Card Title</h4>
            <p>Card content with DARK text (overridden)</p>
        </div>
    </div>
</div>
```
**Background:** linear-gradient(135deg, #0e5881 0%, #0a4563 100%) (dark blue)
**Text Color:** white
**Cards Inside Price-Box:** Override to use dark text (#333) on light backgrounds

## Card Components

### Standard Card (Light Gray) - Secondary Content Container
```html
<div class="card">
    <h4>Card Title</h4>
    <p>Card content...</p>
</div>
```
**Background:** #f9f9f9 (light gray)
**Border:** 4px solid #ffcc33 (gold, left side - brand accent)
**Text Color:** #333 (dark gray)

**Usage:** Use for grouped content, feature lists, service breakdowns, and timeline items

### Card Grid
```html
<div class="card-grid">
    <div class="card">...</div>
    <div class="card">...</div>
    <div class="card">...</div>
</div>
```
**Layout:** Responsive grid (auto-fit, minmax(280px, 1fr))
**Gap:** 20px

## Content Generation Guidelines

### When Using generate_sections.py Template

1. **Import the template:**
   ```bash
   cp ~/AI/TOOLS/mediaforce-proposal-generator/examples/generate_sections_template.py ~/AI/CLIENT_NAME/generate_sections.py
   ```

2. **Customize for client:**
   - Update metadata references
   - Adjust section content
   - Keep color contrast rules intact
   - Use official asset URLs
   - **Use only info-box (light blue) or cards (light gray) for sections**
   - Avoid yellow, green, or orange backgrounds

3. **Platform logos:**
   - Include Google Ads logo if Google Ads is enabled
   - Follow the platform badge pattern
   - Use exact URLs from official assets

4. **Color scheme:**
   - All highlighted sections: `<div class="info-box">`
   - All grouped content: `<div class="card">` within `<div class="card-grid">`
   - Gold accents appear in card borders automatically
   - Never use success-box, warning-box, or highlight-box classes

### When Using proposal_generator.py (AI-based)

The AI generator has been configured with:
- Official asset URLs in SYSTEM_MESSAGE
- Platform logo classes and patterns
- Color contrast rules
- Approved HTML tags and classes

The AI will automatically:
- Use official logos
- Follow color contrast rules
- Apply proper styling classes

## Responsive Design

All proposals are mobile-responsive:
- Desktop: 1200px max width
- Tablet: Adjusted font sizes and spacing
- Mobile: Single-column layout, hamburger menu

## Export Guidelines

### PDF Export
1. Open HTML in browser
2. File → Print → Save as PDF
3. Ensure margins are correct
4. Verify all logos load correctly

### HTML Delivery
- Single-file HTML with embedded CSS
- All assets reference CDN URLs (no local files)
- Works in all modern browsers

## Checklist for New Proposals

- [ ] Body text is 11pt
- [ ] Dark backgrounds have white text
- [ ] Light backgrounds have dark text (#333)
- [ ] Only light blue (info-box) or light gray (cards) used for section backgrounds
- [ ] No yellow, green, or orange background colors (brand focus: blue + gold only)
- [ ] Platform logos use official CDN URLs
- [ ] Google Ads logo appears if Google Ads enabled
- [ ] All cards inside price-boxes have dark text overrides
- [ ] Mediaforce logo is correct URL
- [ ] Gold accents (#ffcc33) used for borders and highlights
- [ ] Proposal passes accessibility contrast checks
- [ ] Mobile responsive layout works
- [ ] PDF export looks professional

## Common Mistakes to Avoid

❌ **Don't:** Use dark text on dark backgrounds
✅ **Do:** Use white text on dark blue backgrounds

❌ **Don't:** Use yellow, green, or orange background colors for sections
✅ **Do:** Use only light blue (info-box) or light gray (cards) for section backgrounds

❌ **Don't:** Use custom/local logo files
✅ **Do:** Use official CDN URLs for all logos

❌ **Don't:** Change font size back to 10pt
✅ **Do:** Keep body text at 11pt

❌ **Don't:** Create platform logos as SVG inline
✅ **Do:** Use official logo images from CDN

❌ **Don't:** Forget to override card text color in price-boxes
✅ **Do:** Add `.price-box .card { color: #333; }` rules

❌ **Don't:** Mix multiple bright background colors (yellow, green, orange)
✅ **Do:** Maintain brand focus with blue primary + gold accents only

## Updates and Maintenance

When updating styles:
1. Update `/Users/mediaforceai/AI/TOOLS/mediaforce-proposal-generator/templates/proposal.css`
2. Update this style guide
3. Test with sample proposal
4. Update `generate_sections_template.py` if needed
5. Document changes in README.md

---

## Version History

### v1.1 - 2025-11-04

**Timeline Updates:**
- Compressed timeline from 4 weeks to 3 weeks
- Campaign launch now in Week 3 (Final QA & Campaign Launch)
- Weeks 4-12 for ongoing optimization
- Updated generate_sections_template.py and metadata_template.json

**Visual & Design:**
- Target audience: Replaced image layout with three horizontal cards
- Added icons: 👥 Demographics, 🎯 Psychographics & Behaviors, 🔍 Search Behavior
- Vision for Success: Two side-by-side cards (🎯 Short-Term Goals, 🚀 Long-Term Vision)
- Creative Services: Added icons 🎨 Google Ads Creative, 📄 Landing Pages, 📊 Ongoing Optimization
- Investment Overview: Google Ads logo (150px) at top of pricing section
- Contact section: Streamlined to centered inline design with icons (📧 📞 🌐) - 70% less space
- Added winter icon (❄️) to Peak Season Readiness section
- Documented seasonal icon patterns (🏖️ summer, 🎃 fall, 🎄 Christmas)

**Color Scheme Simplification:**
- Removed: highlight-box (yellow), success-box (green), warning-box (orange)
- Now using: info-box (light blue) and cards (light gray) exclusively
- Brand focus: Blue primary (#0e5881) + Gold accents (#ffcc33) only
- All templates updated to use info-box for highlighted sections

**Documentation:**
- Added "Simplified Color Scheme" section
- Updated Content Generation Guidelines
- Enhanced checklist with color scheme requirements
- Added common mistakes for color usage
- Updated all examples to use info-box
- Documented Target Audience and Creative Services icon patterns

### v1.0 - Initial Release
- BMW-style proposal format
- Original 4-week timeline
- Multiple colored boxes (blue, yellow, green, orange)
- Target audience image at 45% width
- Initial style guidelines

---

**Last Updated:** 2025-11-04
**Version:** 1.1
**Maintained by:** Mediaforce Team
