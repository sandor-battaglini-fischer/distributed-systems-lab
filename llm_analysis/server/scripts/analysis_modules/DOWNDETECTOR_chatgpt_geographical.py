import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from pathlib import Path
import logging
import json
from typing import Optional, Dict, List, Any
from requests.exceptions import RequestException
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownDetectorAPIClient:
    """Client for interacting with DownDetector API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://downdetectorapi.com/v2"
        self.api_key = api_key or self._get_api_key()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        })

    def _get_api_key(self) -> str:
        """Get API key from environment variable or .env file"""
        env_locations = [
            Path("server/scripts/.env")
        ]
        
        for env_path in env_locations:
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"Loaded environment from {env_path}")
                break
        
        api_key = os.getenv('DOWNDETECTOR_API_KEY')
        if not api_key:
            raise ValueError(
                "DownDetector API key not found in environment. "
                "Please ensure DOWNDETECTOR_API_KEY is set in your .env file"
            )
        return api_key

    def test_connection(self) -> bool:
        """Test API connection and authentication"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False

    def get_available_sites(self) -> List[Dict[str, Any]]:
        """Get list of available sites/companies"""
        try:
            response = self.session.get(f"{self.base_url}/sites")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get available sites: {str(e)}")
            return []

    def get_countries(self) -> List[Dict[str, Any]]:
        """Get list of available countries"""
        try:
            response = self.session.get(f"{self.base_url}/geo/countries")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get countries: {str(e)}")
            return []

    def get_outage_data(self, company_id: str, country_code: str, 
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Get outage data for a specific company and country"""
        try:
            params = {
                'country': country_code,
            }
            
            if start_time:
                params['start_time'] = start_time.isoformat()
            if end_time:
                params['end_time'] = end_time.isoformat()

            response = self.session.get(
                f"{self.base_url}/problems/{company_id}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get outage data for {company_id} in {country_code}: {str(e)}")
            return None

class ChatGPTGlobalOutages:
    def __init__(self):
        self.api_client = DownDetectorAPIClient()
        self.chatgpt_id = self._get_chatgpt_id()
        self.countries = self._get_available_countries()
        self.data_dir = Path("data/chatgpt_outages")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_chatgpt_id(self) -> str:
        """Get ChatGPT's company ID from available sites"""
        sites = self.api_client.get_available_sites()
        for site in sites:
            if site['name'].lower() == 'chatgpt':
                return site['id']
        raise ValueError("ChatGPT not found in available sites")

    def _get_available_countries(self) -> Dict[str, str]:
        """Get available countries and their codes"""
        countries = self.api_client.get_countries()
        return {country['code']: country['name'] for country in countries}

    def test_api_access(self) -> Dict[str, bool]:
        """Test various API functionalities"""
        test_results = {
            'connection': False,
            'sites_access': False,
            'countries_access': False,
            'data_access': False
        }
        
        try:
            # Test basic connection
            test_results['connection'] = self.api_client.test_connection()
            
            # Test sites endpoint
            sites = self.api_client.get_available_sites()
            test_results['sites_access'] = len(sites) > 0
            
            # Test countries endpoint
            countries = self.api_client.get_countries()
            test_results['countries_access'] = len(countries) > 0
            
            # Test data access for one country
            if self.countries:
                test_country = next(iter(self.countries))
                data = self.api_client.get_outage_data(
                    self.chatgpt_id,
                    test_country,
                    datetime.now() - timedelta(days=1),
                    datetime.now()
                )
                test_results['data_access'] = data is not None
            
        except Exception as e:
            logger.error(f"API test failed: {str(e)}")
        
        return test_results

    def fetch_country_data(self, country_code: str, days_back: int = 30) -> Optional[pd.DataFrame]:
        """Fetch ChatGPT outage data for a specific country"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        data = self.api_client.get_outage_data(
            self.chatgpt_id,
            country_code,
            start_time,
            end_time
        )
        
        if data and 'reports' in data:
            df = pd.DataFrame(data['reports'])
            df['country'] = country_code
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        return None

    def collect_all_countries(self) -> Optional[pd.DataFrame]:
        """Collect data from all countries and save to CSV"""
        all_data = []
        
        for country_code in self.countries.keys():
            logger.info(f"Fetching data for {country_code}")
            country_data = self.fetch_country_data(country_code)
            
            if country_data is not None:
                all_data.append(country_data)
            
            time.sleep(2)  # Rate limiting
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.data_dir / f"chatgpt_outages_{timestamp}.csv"
            combined_df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
            return combined_df
        return None

    def generate_comparison_plots(self, df):
        """Generate comparison plots from the collected data"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Set style
        plt.style.use('seaborn')
        
        # 1. Reports by Country
        plt.figure(figsize=(12, 6))
        country_counts = df.groupby('country')['reports'].sum()
        country_counts.plot(kind='bar')
        plt.title('Total ChatGPT Reports by Country')
        plt.xlabel('Country')
        plt.ylabel('Total Reports')
        plt.tight_layout()
        plt.savefig(self.data_dir / 'reports_by_country.png')
        plt.close()
        
        # 2. Time Series Plot
        plt.figure(figsize=(15, 8))
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            plt.plot(country_data['timestamp'], country_data['reports'], 
                    label=self.countries[country], alpha=0.7)
        
        plt.title('ChatGPT Outage Reports Over Time by Country')
        plt.xlabel('Time')
        plt.ylabel('Number of Reports')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(self.data_dir / 'time_series_comparison.png')
        plt.close()
        
        # 3. Heatmap of outage patterns
        pivot_df = df.pivot_table(
            index=df['timestamp'].dt.hour,
            columns='country',
            values='reports',
            aggfunc='mean'
        )
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_df, cmap='YlOrRd', annot=True, fmt='.0f')
        plt.title('Average Reports by Hour and Country')
        plt.xlabel('Country')
        plt.ylabel('Hour of Day')
        plt.tight_layout()
        plt.savefig(self.data_dir / 'hourly_heatmap.png')
        plt.close()

def run_analysis(test_api: bool = True):
    """Run the analysis with optional API testing"""
    analyzer = ChatGPTGlobalOutages()
    
    if test_api:
        test_results = analyzer.test_api_access()
        logger.info("API Test Results:")
        for test, result in test_results.items():
            logger.info(f"{test}: {'✓' if result else '✗'}")
        
        if not all(test_results.values()):
            logger.error("API tests failed. Check your API key and access.")
            return False
    
    df = analyzer.collect_all_countries()
    if df is not None:
        analyzer.generate_comparison_plots(df)
        return True
    return False

if __name__ == "__main__":
    run_analysis() 