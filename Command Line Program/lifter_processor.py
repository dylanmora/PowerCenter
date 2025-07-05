"""Handles all lifter-related processing logic"""

import pandas as pd
import concurrent.futures
import threading
import logging
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from LifterInfo import LifterInfo

class LifterProcessor:
    """Handles all lifter extraction, processing, and data enrichment"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.driver = None
        self.driver_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Initialize Chrome driver for web scraping"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--log-level=3') 
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.logger.info("Chrome driver initialized")
    
    def extract_lifters_with_divisions(self, url: str) -> list:
        """Extract lifters and their divisions in one page load"""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'session-content'))
            )
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Extract both lifter info and division data in one pass
            return self._parse_lifters_with_divisions(soup)
            
        except Exception as e:
            self.logger.error(f"Error extracting lifters from page: {e}")
            return []
    
    def _parse_lifters_with_divisions(self, soup: BeautifulSoup) -> list:
        """Parse lifters and divisions from the main roster page"""
        lifter_data_list = []
        seen_lifter_links = set()
        
        # Find all session containers
        session_containers = soup.find_all('div', class_='session-content')
        
        for session_container in session_containers:
            # Look for division information in the session header
            session_header = session_container.find_previous_sibling('h3') or session_container.find_previous_sibling('h2')
            session_division = session_header.get_text(strip=True) if session_header else "Division not found"
            
            # Find all lifter links in this session
            lifter_links = session_container.select('li a[href]')
            
            for lifter_link in lifter_links:
                lifter_info = self._parse_lifter_link_with_division(lifter_link, seen_lifter_links, session_division)
                if lifter_info:
                    lifter_data_list.append(lifter_info)
                    seen_lifter_links.add(lifter_info[3])
        
        self.logger.info(f"Found {len(lifter_data_list)} lifters to process")
        return lifter_data_list
    
    def _parse_lifter_link_with_division(self, lifter_link, seen_links: set, division: str) -> tuple:
        """Parse lifter link with division info"""
        lifter_name_with_number = lifter_link.text.strip()
        lifter_profile_url = lifter_link['href']
        
        if not self._is_valid_lifter_link(lifter_profile_url, lifter_name_with_number):
            return None
        
        if lifter_profile_url in seen_links:
            return None
        
        clean_lifter_name = self._extract_clean_name(lifter_name_with_number)
        if not clean_lifter_name:
            return None
        
        lifter_name_for_url = clean_lifter_name.replace(' ', '').replace(',', '')
        
        # Include division in the tuple
        return (lifter_name_with_number, clean_lifter_name, lifter_name_for_url, lifter_profile_url, division)
    
    def _is_valid_lifter_link(self, url: str, name: str) -> bool:
        """Validate if link is a proper lifter link"""
        return (url and name and 
                not url.startswith('#') and 
                'javascript:' not in url and
                re.search(r'\d+', name))
    
    def _extract_clean_name(self, name_with_number: str) -> str:
        """Extract clean name from numbered format (e.g., '1 - John Doe' -> 'John Doe')"""
        name_match = re.search(r'\d+\s*[-–]\s*(.+)', name_with_number)
        if name_match:
            clean_name = name_match.group(1).strip()
        else:
            clean_name = re.sub(r'^\d+\s*[-–]?\s*', '', name_with_number).strip()
        
        return clean_name if len(clean_name) >= 2 else None
    
    def process_lifters(self, lifter_data_list: list, max_workers: int = 3) -> list:
        """Process all lifters concurrently and return results"""
        if not lifter_data_list:
            return []
        
        competitors = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_lifter = {
                executor.submit(self._process_single_lifter, lifter_data): lifter_data 
                for lifter_data in lifter_data_list
            }
            
            for future in concurrent.futures.as_completed(future_to_lifter):
                try:
                    result = future.result()
                    if result:
                        competitors.append(result)
                except Exception as e:
                    lifter_data = future_to_lifter[future]
                    self.logger.error(f"Error processing lifter {lifter_data[1]}: {e}")
        
        self.logger.info(f"Successfully processed {len(competitors)} lifters")
        return competitors
    
    def _process_single_lifter(self, lifter_data: tuple) -> LifterInfo:
        """Process a single lifter with performance data and division info"""
        lifter_name_with_number, clean_lifter_name, lifter_name_for_url, lifter_profile_url, division = lifter_data
        
        self.logger.info(f"Processing: {clean_lifter_name}")
        
        # Get performance data from cached OpenPowerlifting data
        powerlifting_data = self.data_manager.get_lifter_stats_robust(lifter_name_for_url)
        
        # Create lifter object
        powerlifter = LifterInfo(
            lifter_name_for_url, 
            lifter_profile_url, 
            powerlifting_data['squat_kg'],
            powerlifting_data['bench_kg'],
            powerlifting_data['deadlift_kg'],
            powerlifting_data['total'],
            powerlifting_data['dotscore'],
            division
        )
        
        # Log processing results
        self._log_lifter_results(clean_lifter_name, division, powerlifting_data)
        
        return powerlifter
    
    def _log_lifter_results(self, name: str, division: str, powerlifting_data: dict):
        """Log detailed results for processed lifter"""
        if powerlifting_data['found']:
            confidence = powerlifting_data.get('confidence', 'unknown')
            self.logger.info(f"Completed: {name} - Division: {division} - Confidence: {confidence}")
            
            if 'warning' in powerlifting_data:
                self.logger.warning(f"Warning for {name}: {powerlifting_data['warning']}")
            
            if 'alternatives' in powerlifting_data:
                self.logger.info(f"Found {len(powerlifting_data['alternatives'])} alternative matches for {name}")
        else:
            self.logger.info(f"Completed: {name} - Division: {division} - No OpenPowerlifting data found")
    
    def create_results_dataframe(self, competitors: list) -> pd.DataFrame:
        """Create formatted DataFrame from processed competitors"""
        if not competitors:
            return pd.DataFrame()
        
        # Convert lifter objects to dictionaries
        competitor_dicts = [vars(pl) for pl in competitors]
        
        # Create DataFrame with proper column order
        df = pd.DataFrame(competitor_dicts, columns=[
            'name', 'squat_kg', 'squat_lbs', 'bench_kg', 'bench_lbs', 
            'deadlift_kg', 'deadlift_lbs', 'dotscore', 'total', 'division'
        ])
        
        # Rename columns for better readability
        df = df.rename(columns={
            'name': 'Lifter Name',
            'squat_kg': 'Squat (kg)',
            'squat_lbs': 'Squat (lbs)',
            'bench_kg': 'Bench (kg)',
            'bench_lbs': 'Bench (lbs)',
            'deadlift_kg': 'Deadlift (kg)',
            'deadlift_lbs': 'Deadlift (lbs)',
            'dotscore': 'Dot Score',
            'total': 'Total',
            'division': 'Division'
        })
        
        # Sort by Dot Score (highest first)
        return df.sort_values(by='Dot Score', ascending=[False])
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Chrome driver closed") 