#!/usr/bin/env python3
"""
Debug script to test lifter name parsing
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_lifter_names():
    """Debug the lifter name parsing"""
    url = "https://liftingcast.com/meets/ma6ev1hf1csd/roster"
    
    print(f"Testing URL: {url}")
    print("=" * 60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Find session containers
            session_containers = soup.find_all('div', class_='session-content')
            print(f"\nFound {len(session_containers)} session-content containers")
            
            for i, session in enumerate(session_containers):
                print(f"\n--- Session {i+1} ---")
                
                # Find lifter links
                lifter_links = session.select('li a[href]')
                print(f"Found {len(lifter_links)} lifter links")
                
                for j, link in enumerate(lifter_links[:5]):  # Show first 5
                    name = link.text.strip()
                    href = link['href']
                    
                    print(f"\nLink {j+1}:")
                    print(f"  Name: '{name}'")
                    print(f"  URL: '{href}'")
                    
                    # Test validation
                    has_url = bool(href)
                    has_name = bool(name)
                    not_hash = not href.startswith('#') if href else True
                    not_javascript = 'javascript:' not in href if href else True
                    has_number = bool(re.search(r'\d+', name)) if name else False
                    
                    print(f"  Validation: URL={has_url}, Name={has_name}, NotHash={not_hash}, NotJS={not_javascript}, HasNumber={has_number}")
                    
                    # Test name extraction
                    name_match = re.search(r'\d+\s*[-–]\s*(.+)', name)
                    if name_match:
                        clean_name = name_match.group(1).strip()
                        print(f"  Clean name (regex): '{clean_name}'")
                    else:
                        clean_name = re.sub(r'^\d+\s*[-–]?\s*', '', name).strip()
                        print(f"  Clean name (fallback): '{clean_name}'")
                    
                    print(f"  Final clean name: '{clean_name}'")
                    print(f"  Valid: {len(clean_name) >= 2 if clean_name else False}")
                    
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_lifter_names() 