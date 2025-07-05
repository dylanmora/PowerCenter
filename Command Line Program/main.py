"""Main orchestration file - coordinates the powerlifting meet analysis process"""

from data_manager import OpenPowerliftingDataManager
from lifter_processor import LifterProcessor

def main():
    """Main execution function - orchestrates the entire meet analysis workflow"""
    
    # Step 1: Initialize and prepare data management system
    # This handles downloading OpenPowerlifting data, caching, and updates
    data_manager = OpenPowerliftingDataManager()
    data_manager.update_if_needed()  # Downloads new data if needed (115MB CSV)
    
    # Step 2: Initialize lifter processing system
    # This sets up Chrome driver for web scraping LiftingCast
    lifter_processor = LifterProcessor(data_manager)
    lifter_processor.setup_driver()
    
    try:
        # Step 3: Define the meet URL to analyze
        meet_url = 'https://liftingcast.com/meets/myvopqy3segb/roster'
        
        # Step 4: Extract lifter information from LiftingCast meet page
        # This scrapes the roster to get all lifter names and profile URLs
        lifter_data_list = lifter_processor.extract_lifters_with_divisions(meet_url)
        
        if lifter_data_list:
            # Step 5: Process all lifters concurrently
            # This combines cached OpenPowerlifting data with live LiftingCast division data
            competitors = lifter_processor.process_lifters(lifter_data_list)
            
            # Step 6: Create formatted results DataFrame
            # Sorts by Dot Score and formats for display/saving
            results = lifter_processor.create_results_dataframe(competitors)
            
            if not results.empty:
                # Step 7: Display and save results
                print("\nTop 10 Lifters by Dot Score:")
                print(results.head(10))
                results.to_csv('meet_results.csv', index=False)
                print(f"\nResults saved to meet_results.csv")
            else:
                print("No results found")
        else:
            print("No lifters found on page")
            
    finally:
        # Step 8: Cleanup resources
        # Always close the Chrome driver to free system resources
        lifter_processor.cleanup()

if __name__ == "__main__":
    main() 