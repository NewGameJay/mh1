#!/usr/bin/env python3
"""
Demand Curve Extraction Runner

Usage:
    # From prompt
    python extract_demandcurve.py "Extract all courses"

    # From job file
    python extract_demandcurve.py --job demandcurve-job.yaml

    # Interactive
    python extract_demandcurve.py
"""

import sys
from pathlib import Path

# Add skills to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.bright_crawler import BrightCrawler


def main():
    output_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        if sys.argv[1] == "--job":
            # Run from job file
            job_file = sys.argv[2] if len(sys.argv) > 2 else "demandcurve-job.yaml"
            crawler = BrightCrawler(session="dc", headed=True, output_dir=str(output_dir))
            result = crawler.run_file(job_file)
            print(f"Extracted {len(result.get('files', []))} files")
            if result.get('errors'):
                print(f"Errors: {result['errors']}")
        else:
            # Run from prompt
            prompt = " ".join(sys.argv[1:])
            crawler = BrightCrawler(session="dc", headed=True, output_dir=str(output_dir))
            result = crawler.run(prompt)
            print(result)
    else:
        # Interactive mode - show example usage
        print("""
Demand Curve Extraction

Examples:
    # Extract all courses
    python extract_demandcurve.py "Extract all 49 courses from Demand Curve.
    Login: vbp615@gmail.com / Temp1pass!
    Save to: demandcurve-courses/"

    # Run full job
    python extract_demandcurve.py --job demandcurve-job.yaml

    # Extract specific content
    python extract_demandcurve.py "Extract 10 newsletters from demandcurve.com/newsletter-vault"
""")


if __name__ == "__main__":
    main()
