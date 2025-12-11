#!/usr/bin/env python3
"""
Initialize a new client proposal project
Creates directory structure and metadata template
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


def init_project(client_name: str, output_dir: Path = None):
    """Initialize a new proposal project for a client"""

    # Convert client name to CAPS with underscores
    safe_name = client_name.upper().replace(' ', '_').replace('/', '_')

    # Default to ~/AI/CLIENT_NAME/
    if output_dir is None:
        output_dir = Path.home() / 'AI' / safe_name
    else:
        output_dir = Path(output_dir) / safe_name

    # Create directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy template metadata
    template_path = Path(__file__).parent / 'examples' / 'metadata_template.json'
    metadata_path = output_dir / 'metadata.json'

    if template_path.exists():
        with open(template_path) as f:
            template = json.load(f)

        # Update with client name and date
        template['metadata']['client_name'] = client_name
        template['metadata']['proposal_date'] = datetime.now().strftime('%Y-%m-%d')

        # Write to project
        with open(metadata_path, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"✅ Created proposal project for: {client_name}")
        print(f"📁 Location: {output_dir}")
        print(f"📝 Edit metadata.json to customize the proposal")
        print(f"\nNext steps:")
        print(f"1. Edit: {metadata_path}")
        print(f"2. Run: python3 proposal_generator.py {output_dir} {output_dir}/Proposal.html")
    else:
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)

    return output_dir


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 init_project.py <client_name> [output_directory]")
        print("\nExample:")
        print("  python3 init_project.py 'Acme Corporation'")
        print("  python3 init_project.py 'BMW Dealership' ~/Documents/Proposals")
        sys.exit(1)

    client_name = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    init_project(client_name, output_dir)


if __name__ == '__main__':
    main()
