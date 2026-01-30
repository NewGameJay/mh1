"""
DataForSEO Collection Template

This script fetches data from DataForSEO API.
Supports SERP (Search Engine Results Page) and Keyword Data.
"""

import sys
import io
import json
import csv
import requests
import time
from datetime import datetime
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURATION
# ============================================================================

# API Credentials
# Provided Base64: am9zZXBoLnF1ZXNhZGFAbWFya2V0ZXJoaXJlLmNvbToxMzk1OGIyNzNkNjZmMDEw
AUTH_HEADER = "Basic am9zZXBoLnF1ZXNhZGFAbWFya2V0ZXJoaXJlLmNvbToxMzk1OGIyNzNkNjZmMDEw"

# Task Parameters
KEYWORDS = [
    "marketing automation",
    "fractional cmo",
]

LOCATION_CODE = 2840  # United States
LANGUAGE_CODE = "en"  # English

# Options: "serp" or "keywords"
TASK_TYPE = "serp" 

# Output
OUTPUT_DIR = Path("outputs/DataForSEO")
PROJECT_NAME = "market_research"

# ============================================================================
# API FUNCTIONS
# ============================================================================

def get_serp_data(keywords, location_code, language_code):
    """Fetch Google Organic SERP data (Live)."""
    url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    
    post_data = []
    for keyword in keywords:
        post_data.append({
            "language_code": language_code,
            "location_code": location_code,
            "keyword": keyword,
            "depth": 20  # Top 20 results
        })
    
    headers = {
        'Authorization': AUTH_HEADER,
        'Content-Type': 'application/json'
    }
    
    print(f"Requesting SERP data for {len(keywords)} keywords...")
    response = requests.post(url, json=post_data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def process_serp_results(results):
    """Extract relevant data from SERP results."""
    processed_data = []
    
    if not results or 'tasks' not in results:
        return processed_data
        
    for task in results['tasks']:
        if task['status_code'] == 20000 and task.get('result'):
            keyword = task['data']['keyword']
            
            for result_item in task['result'][0]['items']:
                if result_item['type'] == 'organic':
                    processed_data.append({
                        'keyword': keyword,
                        'rank_group': result_item.get('rank_group'),
                        'rank_absolute': result_item.get('rank_absolute'),
                        'title': result_item.get('title'),
                        'url': result_item.get('url'),
                        'domain': result_item.get('domain'),
                        'description': result_item.get('description')
                    })
    
    return processed_data

def main():
    print("=" * 80)
    print("DATAFORSEO DATA COLLECTION")
    print("=" * 80)
    
    # Create output dir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if TASK_TYPE == "serp":
        # Get Data
        raw_data = get_serp_data(KEYWORDS, LOCATION_CODE, LANGUAGE_CODE)
        
        if raw_data:
            # Process
            clean_data = process_serp_results(raw_data)
            
            # Export CSV
            csv_file = OUTPUT_DIR / f"{PROJECT_NAME}_serp_{timestamp}.csv"
            
            if clean_data:
                fieldnames = clean_data[0].keys()
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(clean_data)
                print(f"✅ Exported {len(clean_data)} results to {csv_file}")
            else:
                print("⚠️ No organic results found")
                
            # Save Raw JSON (optional, for debugging)
            json_file = OUTPUT_DIR / f"{PROJECT_NAME}_serp_raw_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2)
                
    elif TASK_TYPE == "keywords":
        print("Keyword data collection not yet implemented in this template.")
    
    print("\nDone.")

if __name__ == "__main__":
    main()



