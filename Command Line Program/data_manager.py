import pandas as pd
import requests
import os
import hashlib
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, Tuple, List
import zipfile
import io
from difflib import SequenceMatcher

class OpenPowerliftingDataManager:
    """
    Manages OpenPowerlifting CSV data: download, preprocessing, caching, and lookup
    """
    
    #Constructor, self refers to the instance of the class, and cache_dir is defaulted to "data_cache" unless otherwise specified. 
    def __init__(self, cache_dir: str = "data_cache"):
        self.cache_dir = cache_dir
        self.data_file = os.path.join(cache_dir, "openpowerlifting_data.parquet")
        self.metadata_file = os.path.join(cache_dir, "metadata.json")
        self.index_file = os.path.join(cache_dir, "name_index.json")
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Pandas dataframe for data storage
        self._data = None
        # Name index for fast lookup, data structure is a dictionary with the key being the normalized name 
        self._name_index = {}
        
    def _get_file_hash(self, url: str) -> str:
        """Get ETag or Last-Modified header to check if file has changed"""
        try:
            response = requests.head(url, timeout=10)
            etag = response.headers.get('ETag', '')
            last_modified = response.headers.get('Last-Modified', '')
            return f"{etag}_{last_modified}"
        except Exception as e:
            self.logger.warning(f"Could not get file hash: {e}")
            return ""
    
    def _load_metadata(self) -> Dict:
        """Load metadata from cache"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load metadata: {e}")
        return {}
    
    def _save_metadata(self, metadata: Dict):
        """Save metadata to cache"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f)
        except Exception as e:
            self.logger.error(f"Could not save metadata: {e}")
    
    def needs_update(self) -> bool:
        """Check if data needs to be updated"""
        metadata = self._load_metadata()
        
        # If no cached data exists, we need to download
        if not os.path.exists(self.data_file):
            return True
        
        # Check if it's been more than 24 hours since last update
        last_update = metadata.get('last_update')
        if last_update:
            last_update_dt = datetime.fromisoformat(last_update)
            if datetime.now() - last_update_dt > timedelta(hours=24):
                return True
        
        # Check if remote file has changed
        current_hash = self._get_file_hash("https://openpowerlifting.gitlab.io/opl-csv/files/openpowerlifting-latest.zip")
        cached_hash = metadata.get('file_hash', '')
        
        return current_hash != cached_hash
    
    def download_data(self) -> bool:
        """Download and extract the latest OpenPowerlifting data"""
        try:
            self.logger.info("Downloading OpenPowerlifting data...")
            
            # Download the zip file
            url = "https://openpowerlifting.gitlab.io/opl-csv/files/openpowerlifting-latest.zip"
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Extract CSV from zip
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # Find the CSV file in the zip
                csv_filename = None
                for filename in zip_file.namelist():
                    if filename.endswith('.csv'):
                        csv_filename = filename
                        break
                
                if not csv_filename:
                    raise ValueError("No CSV file found in zip")
                
                # Read CSV directly from zip
                with zip_file.open(csv_filename) as csv_file:
                    df = pd.read_csv(csv_file)
            
            # Save as parquet for better performance
            df.to_parquet(self.data_file, index=False)
            
            # Update metadata
            metadata = {
                'last_update': datetime.now().isoformat(),
                'file_hash': self._get_file_hash(url),
                'rows': len(df),
                'columns': list(df.columns)
            }
            self._save_metadata(metadata)
            
            self.logger.info(f"Successfully downloaded {len(df):,} records")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download data: {e}")
            return False
    
    def _safe_float_conversion(self, value, default=0.0):
        """Safely convert value to float, handling special cases"""
        if value is None or value == '':
            return default
        
        # Convert to string and clean up
        value_str = str(value).strip()
        
        # Handle special cases
        if value_str == '' or value_str.lower() in ['nan', 'none', 'null']:
            return default
        
        # Handle "100+" format (take the base number)
        if '+' in value_str:
            value_str = value_str.replace('+', '')
        
        # Handle ranges like "100-110" (take the lower bound)
        if '-' in value_str and not value_str.startswith('-'):
            value_str = value_str.split('-')[0]
        
        try:
            return float(value_str)
        except (ValueError, TypeError):
            return default
    
    def preprocess_data(self):
        """Enhanced preprocessing with date calculations"""
        if self._data is None:
            if os.path.exists(self.data_file):
                self._data = pd.read_parquet(self.data_file)
            else:
                raise FileNotFoundError("Data file not found. Run download_data() first.")
        
        self.logger.info("Preprocessing data for efficient lookup...")
        
        # Vectorized operations - much faster than iterrows()
        df = self._data.copy()
        
        # Clean and normalize names vectorized
        df['normalized_name'] = df['Name'].str.strip().str.replace(' ', '').str.lower()
        
        # Vectorized float conversion for all numeric columns
        numeric_columns = ['WeightClassKg', 'Best3SquatKg', 'Best3BenchKg', 'Best3DeadliftKg', 
                          'TotalKg', 'Dots', 'BodyweightKg', 'Age']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Create index using groupby (much faster than manual loop)
        self._name_index = {}
        
        # Group by normalized name and convert to index format
        grouped = df.groupby('normalized_name')
        
        # Pre-calculate days old for all records
        df['days_old'] = (pd.Timestamp.now() - pd.to_datetime(df['Date'], errors='coerce')).dt.days
        df['days_old'] = df['days_old'].fillna(9999)  # Default for missing dates
        
        for normalized_name, group in grouped:
            records = []
            for _, row in group.iterrows():
                records.append({
                    'index': row.name,  # Original index
                    'original_name': row['Name'],
                    'meet_name': row.get('MeetName', ''),
                    'date': row.get('Date', ''),
                    'division': row.get('Division', ''),
                    'weight_class': float(row['WeightClassKg']),
                    'federation': row.get('Federation', ''),
                    'country': row.get('Country', ''),
                    'squat': float(row['Best3SquatKg']),
                    'bench': float(row['Best3BenchKg']),
                    'deadlift': float(row['Best3DeadliftKg']),
                    'total': float(row['TotalKg']),
                    'dotscore': float(row['Dots']),
                    'bodyweight': float(row['BodyweightKg']),
                    'age': float(row['Age']),
                    'days_old': int(row['days_old'])
                })
            self._name_index[normalized_name] = records
        
        # Use pickle instead of JSON for faster I/O
        self._save_index_fast()
        
        self.logger.info(f"Created index for {len(self._name_index)} unique names")

    def _save_index_fast(self):
        """Save index using pickle for better performance"""
        import pickle
        with open(self.index_file.replace('.json', '.pkl'), 'wb') as f:
            pickle.dump(self._name_index, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load_index_fast(self):
        """Load index using pickle for better performance"""
        import pickle
        pickle_file = self.index_file.replace('.json', '.pkl')
        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def load_data(self):
        """Load data and index into memory"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError("Data file not found. Run download_data() first.")
        
        self._data = pd.read_parquet(self.data_file)
        
        # Load name index - try pickle first, then JSON, then rebuild
        self._name_index = self._load_index_fast()  # Try pickle file
        
        if self._name_index is None:
            # Try JSON file as fallback
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r') as f:
                    self._name_index = json.load(f)
            else:
                # No index file exists, rebuild it
                self.preprocess_data()
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names using sequence matching"""
        if len(name1) == 0 or len(name2) == 0:
            return 0.0
        
        # Use SequenceMatcher for better similarity calculation
        return SequenceMatcher(None, name1, name2).ratio()
    
    def _calculate_comprehensive_match_score(self, record: Dict, name_similarity: float, 
                                           current_weight_class: float, meet_name: str = "") -> float:
        """Calculate comprehensive match score using multiple factors"""
        score = 0.0
        
        # Name similarity (50% weight) - increased from 40%
        score += name_similarity * 0.5
        
        # Weight class proximity (30% weight) - increased from 25%
        if record['weight_class'] > 0 and current_weight_class > 0:
            weight_diff = abs(record['weight_class'] - current_weight_class)
            weight_score = max(0, 1 - weight_diff/20)  # Within 20kg
            score += weight_score * 0.3
        
        # Recency (10% weight) - unchanged
        if record['date']:
            try:
                date = datetime.strptime(record['date'], '%Y-%m-%d')
                days_old = (datetime.now() - date).days
                if days_old < 365:  # Within last year
                    score += 0.1
                elif days_old < 1095:  # Within last 3 years
                    score += 0.05
            except:
                pass
        
        # Data completeness (10% weight) - unchanged
        completeness_score = 0
        if record['total'] > 0:
            completeness_score += 0.5
        if record['weight_class'] > 0:
            completeness_score += 0.3
        if record['date']:
            completeness_score += 0.2
        score += completeness_score * 0.1
        
        return score
    
    def find_lifter_candidates(self, name: str, current_weight_class: float = 0, 
                              meet_name: str = "", max_candidates: int = 10) -> List[Dict]:
        """Find multiple potential matches with confidence scores, prioritizing unique exact matches"""
        if not self._name_index:
            self.load_data()
        
        # Try multiple normalization strategies
        search_names = self._try_multiple_normalizations(name)
        candidates = []
        
        # Try each normalization strategy
        for search_name in search_names:
            # Check for exact normalized name match first
            if search_name in self._name_index:
                exact_records = self._name_index[search_name]
                if len(exact_records) == 1:
                    # Only one record: return as high confidence match
                    record = exact_records[0]
                    return [{
                        'record': record,
                        'score': 1.0,
                        'name_similarity': 1.0,
                        'match_type': 'exact'
                    }]
                else:
                    # Multiple records (duplicates): use comprehensive scoring algorithm
                    for record in exact_records:
                        match_score = self._calculate_comprehensive_match_score(
                            record, 1.0, current_weight_class, meet_name
                        )
                        candidates.append({
                            'record': record,
                            'score': match_score,
                            'name_similarity': 1.0,
                            'match_type': 'exact_duplicate'
                        })
                    candidates.sort(key=lambda x: x['score'], reverse=True)
                    return candidates[:max_candidates]
            
            # If no exact match, look for names that start with the search name
            # This handles cases like "RyanJordan" searching for "ryanjordan#1", "ryanjordan#2", etc.
            matching_names = [indexed_name for indexed_name in self._name_index.keys() 
                             if indexed_name.startswith(search_name)]
            
            if matching_names:
                # Found names that start with the search name
                for indexed_name in matching_names:
                    records = self._name_index[indexed_name]
                    for record in records:
                        # Calculate name similarity (should be high since it starts with search name)
                        name_similarity = len(search_name) / len(indexed_name)
                        match_score = self._calculate_comprehensive_match_score(
                            record, name_similarity, current_weight_class, meet_name
                        )
                        candidates.append({
                            'record': record,
                            'score': match_score,
                            'name_similarity': name_similarity,
                            'match_type': 'prefix_match'
                        })
                
                candidates.sort(key=lambda x: x['score'], reverse=True)
                return candidates[:max_candidates]
        
        # No matches found - return empty list
        return []
    
    def get_lifter_stats_robust(self, name: str, current_weight_class: float = 0, 
                               meet_name: str = "") -> Dict:
        """Robust lifter lookup that handles real-world complexity"""
        
        # Find all potential matches
        candidates = self.find_lifter_candidates(name, current_weight_class, meet_name)
        
        # Handle different scenarios
        if not candidates:
            return {
                'found': False,
                'reason': 'no_matches',
                'squat_kg': '0',
                'bench_kg': '0',
                'deadlift_kg': '0',
                'total': '0',
                'dotscore': '0'
            }
        
        if len(candidates) == 1 and candidates[0]['score'] > 0.9:
            # High confidence single match
            record = candidates[0]['record']
            return {
                'found': True,
                'confidence': 'high',
                'squat_kg': str(record['squat']),
                'bench_kg': str(record['bench']),
                'deadlift_kg': str(record['deadlift']),
                'total': str(record['total']),
                'dotscore': str(record['dotscore']),
                'meet_name': record['meet_name'],
                'date': record['date'],
                'division': record['division'],
                'weight_class': record['weight_class'],
                'federation': record['federation'],
                'country': record['country']
            }
        
        if len(candidates) == 1 and candidates[0]['score'] > 0.7:
            # Medium confidence single match
            record = candidates[0]['record']
            return {
                'found': True,
                'confidence': 'medium',
                'squat_kg': str(record['squat']),
                'bench_kg': str(record['bench']),
                'deadlift_kg': str(record['deadlift']),
                'total': str(record['total']),
                'dotscore': str(record['dotscore']),
                'meet_name': record['meet_name'],
                'date': record['date'],
                'division': record['division'],
                'weight_class': record['weight_class'],
                'federation': record['federation'],
                'country': record['country'],
                'warning': 'Possible match, verify accuracy'
            }
        
        # Multiple candidates - return best with alternatives
        best_record = candidates[0]['record']
        alternatives = []
        
        for candidate in candidates[1:4]:  # Next 3 best matches
            alternatives.append({
                'name': candidate['record']['original_name'],
                'meet': candidate['record']['meet_name'],
                'date': candidate['record']['date'],
                'weight_class': candidate['record']['weight_class'],
                'total': candidate['record']['total'],
                'score': candidate['score']
            })
        
        return {
            'found': True,
            'confidence': 'low',
            'squat_kg': str(best_record['squat']),
            'bench_kg': str(best_record['bench']),
            'deadlift_kg': str(best_record['deadlift']),
            'total': str(best_record['total']),
            'dotscore': str(best_record['dotscore']),
            'meet_name': best_record['meet_name'],
            'date': best_record['date'],
            'division': best_record['division'],
            'weight_class': best_record['weight_class'],
            'federation': best_record['federation'],
            'country': best_record['country'],
            'alternatives': alternatives,
            'warning': f'Multiple matches found ({len(candidates)} candidates)'
        }
    
    def get_lifter_stats(self, name: str) -> Dict:
        """Get comprehensive lifter statistics (backward compatibility)"""
        return self.get_lifter_stats_robust(name)
    
    def update_if_needed(self):
        """Check if update is needed and perform it"""
        if self.needs_update():
            self.logger.info("Data update needed")
            if self.download_data():
                self.preprocess_data()
                return True
        else:
            self.logger.info("Data is up to date")
        return False

    def get_lifter_stats_batch(self, names: List[str]) -> Dict[str, Dict]:
        """Batch lookup for multiple lifters"""
        if not self._name_index:
            self.load_data()
        
        results = {}
        
        for name in names:
            # Try multiple normalization strategies
            search_names = self._try_multiple_normalizations(name)
            found = False
            
            for search_name in search_names:
                if search_name in self._name_index:
                    records = self._name_index[search_name]
                    if records:
                        record = records[0]
                        results[name] = {
                            'found': True,
                            'confidence': 'exact',
                            'squat_kg': str(record['squat']),
                            'bench_kg': str(record['bench']),
                            'deadlift_kg': str(record['deadlift']),
                            'total': str(record['total']),
                            'dotscore': str(record['dotscore'])
                        }
                        found = True
                        break
            
            if not found:
                results[name] = self._get_default_response()
        
        return results

    def _get_default_response(self) -> Dict:
        return {
            'found': False,
            'squat_kg': '0',
            'bench_kg': '0',
            'deadlift_kg': '0',
            'total': '0',
            'dotscore': '0'
        }

    def _normalize_search_name(self, name: str) -> str:
        """Normalize search name, handling commas and other special characters"""
        # Remove spaces and commas, convert to lowercase
        return name.replace(' ', '').replace(',', '').lower()

    def _try_multiple_normalizations(self, name: str) -> List[str]:
        """Try multiple normalization strategies for better matching"""
        normalizations = []
        
        # Strategy 1: Remove spaces and commas
        normalizations.append(name.replace(' ', '').replace(',', '').lower())
        
        # Strategy 2: Remove only spaces (for backward compatibility)
        normalizations.append(name.replace(' ', '').lower())
        
        # Strategy 3: Remove only commas
        normalizations.append(name.replace(',', '').lower())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_normalizations = []
        for norm in normalizations:
            if norm not in seen:
                seen.add(norm)
                unique_normalizations.append(norm)
        
        return unique_normalizations 