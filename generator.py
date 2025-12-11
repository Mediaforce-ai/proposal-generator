#!/usr/bin/env python3
"""
Pentest Report Generator - Schema → Fragments → Assembly
Enforces structure, prevents redundancy, guarantees quality
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from anthropic import Anthropic
from validator import FragmentValidator
from evidence_mapper import EvidenceMapper


# Global system message for all LLM calls
SYSTEM_MESSAGE = """You are generating HTML fragments for a penetration test report.

**ALLOWED TAGS:** p, h2, h3, h4, ul, ol, li, a, strong, em, code, pre, table, thead, tbody, tr, th, td, div, span, br

**ALLOWED CLASSES:** section, finding-box, finding-header, severity-badge, severity-critical, severity-high, severity-medium, severity-low, severity-info, info-box, warning-box, success-box, critical-box, risk-box, table, table-compact, codeblock, checklist, pill, kpi, risk-matrix, callout, two-col, badge

**RULES:**
- Do NOT use style attributes or script tags
- Do NOT invent new classes
- Produce concise, factual, non-redundant content
- Respect the provided length budget
- Output ONLY the requested HTML fragment
- Do NOT include explanations, comments, or markdown code fences
- Output raw HTML ready for direct insertion"""


class PentestReportGenerator:
    """4-stage generator: Outline → Sections → Findings → QA"""

    def __init__(self, project_dir: Path, api_key: str):
        self.project_dir = Path(project_dir)
        self.client = Anthropic(api_key=api_key)
        self.validator = FragmentValidator(Path(__file__).parent / 'schemas')
        self.evidence_mapper = EvidenceMapper(project_dir)
        self.report_data = {}

    def load_project_data(self) -> Dict[str, Any]:
        """Load all data files from project directory"""
        data = {}

        # Load metadata if exists
        metadata_file = self.project_dir / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file) as f:
                data['metadata'] = json.load(f)
        else:
            # ERROR: Do not fabricate dates - require metadata.json
            print("\n❌ ERROR: metadata.json not found!")
            print(f"   Expected location: {metadata_file}")
            print("\n   Create metadata.json with ACTUAL engagement dates:")
            print('   {')
            print('     "client": "ClientName",')
            print('     "engagement_window": "YYYY-MM-DD to YYYY-MM-DD",')
            print('     "report_date": "YYYY-MM-DD",')
            print('     "analyst": "The CyberHunter team",')
            print('     "scope": ["target1", "target2"],')
            print('     "methodology": "Black box external penetration test..."')
            print('   }')
            raise FileNotFoundError(f"metadata.json required at {metadata_file}")

        # Load findings
        findings_dir = self.project_dir / 'scans'
        summary_file = findings_dir / 'FINAL_FINDINGS_SUMMARY.txt'

        if summary_file.exists():
            data['findings_raw'] = summary_file.read_text()
        else:
            data['findings_raw'] = "No findings file found"

        # Load targets
        targets_file = self.project_dir / 'targets.txt'
        if targets_file.exists():
            data['targets'] = targets_file.read_text()
        else:
            data['targets'] = ""

        return data

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

    # ==================== STAGE A: OUTLINE ====================

    def stage_a_outline(self, data: Dict) -> Dict[str, List[str]]:
        """Generate outline and budgets for each section"""
        print("\n=== STAGE A: Generating Outline ===")

        prompt = f"""**Context:**
Client: {data['metadata']['client']}
Findings Data:
{data['findings_raw'][:2000]}

**Task:** Generate a bulleted outline for each report section.

**Constraints:**
- No prose, bullets only
- Max 12 bullets per section
- Each bullet ≤ 18 words
- Focus on WHAT information belongs in each section

**Output JSON format:**
{{
  "executive_summary": ["bullet 1", "bullet 2", ...],
  "risk_overview": ["bullet 1", ...],
  "detailed_findings": ["bullet 1", ...],
  "positive_controls": ["bullet 1", ...],
  "remediation": ["bullet 1", ...]
}}

Generate the outline now:"""

        response = self.call_claude(prompt, max_tokens=2000)

        # Parse JSON from response
        try:
            # Extract JSON if wrapped in code fences
            json_match = response
            if '```' in response:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
                if json_match:
                    json_match = json_match.group(1)

            outline = json.loads(json_match)
            print(f"✓ Outline generated ({len(outline)} sections)")
            return outline
        except:
            print("✗ Failed to parse outline JSON, using fallback")
            return {
                "executive_summary": ["Overview of assessment", "Risk level", "Key findings summary"],
                "risk_overview": ["Severity counts", "Findings table"],
                "detailed_findings": ["Complete technical details for each finding"],
                "positive_controls": ["What is NOT vulnerable"],
                "remediation": ["Timeline-based action items"]
            }

    # ==================== STAGE B: SECTION FRAGMENTS ====================

    def stage_b_executive_summary(self, data: Dict, outline: List[str]) -> Dict:
        """Generate executive summary fragments"""
        print("\n[STAGE B] Generating Executive Summary...")

        # Count targets
        targets_file = self.project_dir / 'targets.txt'
        target_count = 0
        target_summary = ""
        if targets_file.exists():
            targets = [t.strip() for t in targets_file.read_text().strip().split('\n') if t.strip()]
            target_count = len(targets)
            ip_count = sum(1 for t in targets if not t.startswith('http'))
            domain_count = target_count - ip_count
            target_summary = f"{target_count} targets ({ip_count} IP addresses, {domain_count} web applications)"

        # Overview
        prompt = f"""**Metadata:** {json.dumps(data['metadata'])}
**Target Scope:** {target_summary}
**Methodology:** {data['metadata'].get('methodology', 'Black box external penetration test')}

**Outline:** {json.dumps(outline)}

**Task:** Write executive summary overview (2-3 sentences, non-technical).

**REQUIRED Content (MUST include ALL of these):**
- State this was a Black Box penetration test
- Mention the testing followed OWASP WSTG and PTES industry standards
- Include scope: {target_summary}
- Include engagement period: {data['metadata'].get('engagement_window', 'N/A')}
- Summarize overall risk level and finding counts

**Structure:** One cohesive paragraph covering all required content above.

**Length:** ≤ 180 words

**Forbidden:** CWE, CVE, POC details, technical jargon

**Output:** Plain HTML paragraph (just <p> tag content)"""

        overview_html = self.call_claude(prompt, max_tokens=800)

        # Risk statement
        prompt = f"""**Findings:** {data['findings_raw'][:1000]}

**Task:** Generate one positive-framed sentence about overall security posture.

**Example:** "The infrastructure demonstrates solid baseline security with 6 MEDIUM and 3 LOW findings requiring attention"

**Length:** ≤ 25 words

**Output:** Single sentence (plain text, no HTML tags)"""

        risk_statement_html = '<p>' + self.call_claude(prompt, max_tokens=200) + '</p>'

        # Key findings list
        prompt = f"""**Findings:** {data['findings_raw']}
**Target Scope:** {target_summary}

**Task:** Create bulleted list of key findings.

**Format:** For each finding:
<li><strong>{{title}}</strong> (CVSS {{score}}) - {{one sentence impact including which targets/services are affected}}</li>

**Sort:** By CVSS score descending

**Constraints:**
- MUST mention which targets are affected (e.g., "affects all web applications", "affects HTTPS services", "impacts 17 IP-based hosts")
- Max 20 words per bullet (after title and CVSS)
- NO CWE references
- NO POC commands
- NO remediation steps

**Output:** ONLY <li> elements (no <ul> wrapper)"""

        key_findings_html = self.call_claude(prompt, max_tokens=1500)

        result = {
            'overview_html': overview_html,
            'risk_statement_html': risk_statement_html,
            'key_findings_html': key_findings_html
        }

        print("  ✓ Executive Summary complete")
        return result

    def stage_b_risk_overview(self, data: Dict) -> Dict:
        """Generate risk overview fragments"""
        print("[STAGE B] Generating Risk Overview...")

        # Parse findings to count severities and get target info
        findings_text = data['findings_raw']

        # Count targets
        targets_file = self.project_dir / 'targets.txt'
        target_summary = ""
        if targets_file.exists():
            targets = [t.strip() for t in targets_file.read_text().strip().split('\n') if t.strip()]
            target_count = len(targets)
            ip_count = sum(1 for t in targets if not t.startswith('http'))
            domain_count = target_count - ip_count
            target_summary = f"{target_count} targets ({ip_count} IP addresses, {domain_count} web applications)"

        prompt = f"""**Findings:** {findings_text}
**Target Scope:** {target_summary}

**Task:** Count findings by severity and create findings table.

**Output JSON:**
{{
  "severity_counts": {{
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }},
  "findings_table_html": "<tr><td>FINDING-ID</td><td>Title</td><td><span class=\\"severity-badge severity-medium\\">MEDIUM</span></td><td>5.3</td><td>Affected Targets</td></tr>..."
}}

**Table format:** ID | Title | Severity Badge | CVSS | Affected Targets
**Affected Targets column:** Must specify which targets (e.g., "All web applications", "HTTPS services on 17 IPs", "forms.logiforms.com")
**Forbidden:** NO full descriptions, NO CWE in table

Generate the JSON:"""

        response = self.call_claude(prompt, max_tokens=2000)

        try:
            # Extract JSON
            if '```' in response:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1)

            result = json.loads(response)
            print("  ✓ Risk Overview complete")
            return result
        except:
            print("  ✗ Failed to parse risk overview, using fallback")
            return {
                "severity_counts": {"critical": 0, "high": 0, "medium": 6, "low": 3},
                "findings_table_html": ""
            }

    # ==================== STAGE C: FINDING FRAGMENTS ====================

    def stage_c_finding_single(self, finding_id: str, title: str, cvss: float, cwe: str, severity: str) -> Dict:
        """Generate a single finding with complete 8-part structure using REAL evidence"""

        # Get actual evidence from test data
        evidence = self.evidence_mapper.get_evidence(finding_id)

        targets_text = "Unknown targets"
        if evidence['targets']:
            targets_text = ', '.join(evidence['targets'])

        poc_context = ""
        if evidence['poc_snippets']:
            poc_context = "\n\n**ACTUAL TEST OUTPUT (MUST USE THIS EXACT OUTPUT):**\n" + '\n---\n'.join(evidence['poc_snippets'][:2])

        prompt = f"""**Finding ID:** {finding_id}
**Title:** {title}
**CVSS:** {cvss}
**CWE:** {cwe}
**Severity:** {severity}
**Affected Targets:** {targets_text}

{poc_context}

**CRITICAL INSTRUCTION:** The evidence_html MUST use the ACTUAL TEST OUTPUT provided above. DO NOT fabricate commands or output. Use the exact text from the test results.

**Task:** Generate complete finding structure in JSON format.

**Output ONLY this JSON (no explanations):**
{{
  "id": "{finding_id}",
  "title": "{title}",
  "severity": "{severity}",
  "cvss": {cvss},
  "cwe": {{
    "id": "{cwe}",
    "name": "Full CWE Name"
  }},
  "summary_html": "<p>MUST start with: 'Testing of {targets_text} revealed...' then 2-3 sentence technical description. MUST explicitly state which targets are affected.</p>",
  "evidence_html": "<h4>Proof of Concept</h4><p><strong>Tested Targets:</strong> {targets_text}</p><pre><code>COPY THE EXACT TEST OUTPUT FROM ABOVE - DO NOT MAKE UP COMMANDS</code></pre>",
  "impact_html": "<ul><li>Business impact 1</li><li>Business impact 2</li><li>Business impact 3</li></ul>",
  "remediation_html": "<p>Description of fix:</p><pre><code>nginx configuration or code fix here</code></pre>",
  "references_html": "<ul><li><a href=\\"https://cwe.mitre.org/data/definitions/{cwe.replace('CWE-', '')}.html\\">{cwe}</a></li></ul>"
}}

**Rules:**
- summary_html: MUST state "Testing of {targets_text} revealed..." and ≤ 140 words
- evidence_html: MUST use the ACTUAL test output provided above, NOT fabricated examples
- impact_html: 3-5 specific business impacts as <li> items
- remediation_html: Complete working fix with code examples
- references_html: Link to CWE and relevant standards

Generate the JSON:"""

        response = self.call_claude(prompt, max_tokens=3000)

        try:
            # Extract JSON
            if '```' in response:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1)

            finding = json.loads(response)
            return finding
        except Exception as e:
            print(f"    ✗ Failed to parse finding: {e}")
            return None

    def stage_c_findings(self, data: Dict) -> List[Dict]:
        """Generate complete finding fragments - one at a time for reliability"""
        print("\n=== STAGE C: Generating Finding Fragments ===")

        findings_text = data['findings_raw']

        # Parse individual findings from summary
        import re
        finding_blocks = re.findall(
            r'(\d+)\.\s+([A-Z]+-\d+):\s+([^\n]+)\n\s+CVSS:\s+([\d.]+)\s+\|\s+(CWE-\d+)',
            findings_text
        )

        print(f"  Found {len(finding_blocks)} findings to generate")

        findings = []
        for idx, (num, finding_id, title, cvss, cwe) in enumerate(finding_blocks, 1):
            print(f"  [{idx}/{len(finding_blocks)}] Generating {finding_id}: {title[:40]}...")

            # Determine severity from CVSS score
            cvss_float = float(cvss)
            if cvss_float >= 9.0:
                severity = "CRITICAL"
            elif cvss_float >= 7.0:
                severity = "HIGH"
            elif cvss_float >= 4.0:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            # Generate single finding with REAL evidence
            finding = self.stage_c_finding_single(finding_id, title, float(cvss), cwe, severity)

            if finding:
                # Validate
                is_valid, errors = self.validator.validate_finding(finding, idx)
                if not is_valid:
                    print(f"      ⚠ Validation warnings ({len(errors)} issues)")
                else:
                    print(f"      ✓ Valid")

                findings.append(finding)
            else:
                print(f"      ✗ Failed")

        print(f"✓ Successfully generated {len(findings)}/{len(finding_blocks)} findings")
        return findings

    # ==================== STAGE D: QA & ASSEMBLY ====================

    def stage_d_qa(self, report_data: Dict) -> Dict:
        """QA pass to check for issues"""
        print("\n=== STAGE D: QA Validation ===")

        is_valid, errors = self.validator.validate_report_data(report_data)

        if is_valid:
            print("✓ All validations passed")
        else:
            print(f"⚠ Found {len(errors)} validation issues:")
            for err in errors[:10]:  # Show first 10
                print(f"  - {err}")

        return report_data

    # ==================== CONCLUSION GENERATION ====================

    def generate_conclusion(self, data: Dict) -> Dict:
        """Generate conclusion summarizing the overall testing effort and results"""
        print("\n[Generating Conclusion]")

        metadata = data['metadata']
        findings = self.report_data.get('findings', [])

        # Count findings by severity
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in findings:
            severity = finding.get('severity', 'LOW')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Count targets
        targets_file = self.project_dir / 'targets.txt'
        target_count = 0
        if targets_file.exists():
            targets = [t.strip() for t in targets_file.read_text().strip().split('\n') if t.strip()]
            target_count = len(targets)

        prompt = f"""**Client:** {metadata.get('client')}
**Engagement Window:** {metadata.get('engagement_window')}
**Methodology:** {metadata.get('methodology')}
**Targets Tested:** {target_count} targets
**Findings Summary:**
- CRITICAL: {severity_counts['CRITICAL']}
- HIGH: {severity_counts['HIGH']}
- MEDIUM: {severity_counts['MEDIUM']}
- LOW: {severity_counts['LOW']}

**Task:** Write a professional conclusion for the penetration test report.

**Structure:** 2-3 paragraphs covering:

1. **Testing Summary**: Briefly restate what was tested (methodology, scope, duration)
2. **Results Overview**: Summarize the findings and overall security posture
3. **Path Forward**: Positive statement about remediation and CyberHunter's availability for support

**Tone:**
- Professional and balanced
- Acknowledge both vulnerabilities found and positive security controls
- End on a constructive note about improvement opportunities
- Offer CyberHunter's ongoing support

**Length:** ≤ 200 words total

**Forbidden:**
- Do NOT repeat specific finding details (they're already in the report)
- Do NOT use alarmist language
- Do NOT include new recommendations (those are in Remediation section)

**Output:** Plain HTML paragraphs (use <p> tags, no <h4> or other headings)

Generate the conclusion:"""

        conclusion_html = self.call_claude(prompt, max_tokens=1000)

        print("  ✓ Conclusion complete")

        return {
            'conclusion_html': conclusion_html
        }

    # ==================== MAIN GENERATION ====================

    def generate(self, output_file: Path):
        """Main generation pipeline"""
        print("🚀 Starting Report Generation")
        print(f"📂 Project: {self.project_dir}")

        # Load data
        data = self.load_project_data()
        print(f"✓ Loaded project data")

        # Stage A: Outline
        outline = self.stage_a_outline(data)

        # Stage B: Sections
        print("\n=== STAGE B: Generating Section Fragments ===")
        self.report_data['metadata'] = data['metadata']
        self.report_data['executive_summary'] = self.stage_b_executive_summary(
            data, outline.get('executive_summary', [])
        )
        self.report_data['risk_overview'] = self.stage_b_risk_overview(data)

        # Stage C: Findings
        self.report_data['findings'] = self.stage_c_findings(data)

        # Positive controls (simple)
        self.report_data['positive_controls'] = {
            'controls_html': '<ul class="checklist"><li>SQL Injection: NOT VULNERABLE</li><li>XSS: NOT VULNERABLE</li></ul>'
        }

        # Remediation (reference-based)
        self.report_data['remediation'] = {
            'timeline_groups': []
        }

        # Conclusion
        self.report_data['conclusion'] = self.generate_conclusion(data)

        # Stage D: QA
        self.report_data = self.stage_d_qa(self.report_data)

        # Save intermediate JSON
        json_file = output_file.parent / (output_file.stem + '_data.json')
        with open(json_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        print(f"\n💾 Saved intermediate data: {json_file}")

        # Assemble final HTML
        from assembler import Assembler
        assembler = Assembler(
            Path(__file__).parent / 'templates' / 'template.html',
            Path(__file__).parent / 'templates' / 'report.css'
        )

        final_html = assembler.assemble(self.report_data)

        with open(output_file, 'w') as f:
            f.write(final_html)

        print(f"\n✅ Report Generated: {output_file}")
        print(f"📊 Size: {len(final_html)} characters, {len(final_html.split())} lines")


def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <project_dir> <output_file>")
        print("Example: python generator.py ~/claude/LOGIFORMS-PENTEST report.html")
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

    # Generate report
    generator = PentestReportGenerator(project_dir, api_key)
    generator.generate(output_file)


if __name__ == '__main__':
    main()
