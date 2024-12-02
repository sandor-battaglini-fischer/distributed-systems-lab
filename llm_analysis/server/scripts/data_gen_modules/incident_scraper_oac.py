import time
import os
import traceback
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.color import Color


from dateutil import parser
from dateutil.tz import gettz
from datetime import timedelta
import pandas as pd
from util_data import read_data, load_json_column, unnest_dict, get_incident_id, write_partitioned_data


def calculate_start_date(end_date):
    start_date = end_date - relativedelta(months=2)
    start_date_str = start_date.strftime("%Y%m")
    end_date_str = end_date.strftime("%Y%m")
    return start_date_str, end_date_str


def get_archive_path(partition):
    start_date, end_date = calculate_start_date(partition)
    archive_folder = f"data/raw/incident/openai"
    os.makedirs(archive_folder, exist_ok=True)
    return f"{archive_folder}/incident_history_{start_date}_{end_date}.csv"


class MyIncidentPage:
    # Class variable for XPaths that do not change across instances
    UPDATE_XPATH = "//div[@class='row update-row']"
    SERVICE_XPATH = "//div[contains(@class, 'components-affected')]"
    INCIDENT_LIST_XPATH = "//a[contains(@class, 'incident-title')]"
    PAGE_XPATH = "(//h4[contains(@class, 'month-title')])[1]"
    PAGINATION_XPATH = "//div[@class='pagination']//i[@class='left-arrow']"
    SHOW_ALL_XPATH = "//div[contains(@class, 'expand-incidents') and @aria-expanded='false']"

    def __init__(self, driver, provider_url):
        self.driver = driver
        self.c_key = MAC_C_KEY
        self.provider_url = provider_url

    def get_incident_updates(self):
        updates = []
        update_rows = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, self.UPDATE_XPATH))
        )
        # get update by rows
        for update_row in update_rows:
            title = update_row.find_element(By.XPATH, ".//div[contains(@class, 'update-title')]").text
            body = update_row.find_element(By.XPATH, ".//div[contains(@class, 'update-body')]").text
            timestamp = update_row.find_element(By.XPATH, ".//div[contains(@class, 'update-timestamp')]").text

            updates.append({
                    "Update_Title": title,
                    "Update_Body": body,
                    "Update_Timestamp": timestamp
            })

        return json.dumps(updates)

    def get_incident_service(self):
        try:
            service = self.driver.find_element(By.XPATH, self.SERVICE_XPATH).text
        except NoSuchElementException:
            service = None
            print("Service element not found, setting service to None.")
        return service

    def switch_to_incident(self, incident, original_window):
        print("Switch to new window: ")
        title = incident.text
        link = incident.get_attribute('href')
        impact = incident.get_attribute('class').split(' ')[0]
        incident_color = Color.from_string(incident.value_of_css_property('color')).hex
        # switch to new tab to collect incident updates
        incident.send_keys(self.c_key + Keys.RETURN)
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        # collect incident updates
        # updates = self.get_incident_updates()
        # service = self.get_incident_service()
        record = pd.DataFrame({
            "Incident_Title": [title],
            "Incident_Link": [link],
            "Incident_color": [incident_color],
            "Incident_Impact": [impact],
            "Updates": [self.get_incident_updates()],
            "Service": [self.get_incident_service()]
        })
        # print(record[0]['Incident_Title'], ". ", json.loads(record[0]['Updates'][0])['Update_Timestamp'])
        print(record['Incident_Title'][0], ". ", json.loads(record['Updates'][0])[0]['Update_Timestamp'])
        # switch back
        self.driver.close()
        self.driver.switch_to.window(original_window)
        return record

    def get_incident_list(self):
        try:
            incident_list = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, self.INCIDENT_LIST_XPATH))
            )
            print("Incidents found in this page: ", len(incident_list))
        except Exception as e:
            print("No incidents found.")
            incident_list = []
        return incident_list

    def archive_incidents(self, incident_df):
        date_str = self.driver.find_element(By.XPATH, self.PAGE_XPATH).text
        date_partition = datetime.strptime(date_str, "%B %Y")
        incident_df.to_csv(get_archive_path(date_partition), index=False)

    def loop_over_incidents(self):
        attempt = 0
        max_attempts = 5
        while attempt < max_attempts:
            incident_df = pd.DataFrame()
            flag_no_data = False
            try:
                # Collecting incident records in new tabs
                incident_list = self.get_incident_list()
                original_window = self.driver.current_window_handle
                if not incident_list:
                    flag_no_data = True
                else:
                    # loop over incidents when there are any
                    for incident_title in incident_list:
                        incident_record = self.switch_to_incident(incident_title, original_window)
                        incident_df = pd.concat([incident_df, pd.DataFrame(incident_record)])
                return incident_df, flag_no_data
            except StaleElementReferenceException:
                print("Stale element, restarting incidents looping process.")
                attempt += 1
                continue
            except Exception as e:
                print("Executing loop_over_incidents(). An error occurred: ", e)
                traceback.print_exc()

        print("\nWarning: this should not happen!!!\n")
        return [], True

    def show_all_incidents(self):
        show_all_buttons = self.driver.find_elements(By.XPATH, self.SHOW_ALL_XPATH)
        if show_all_buttons:
            for show_all in show_all_buttons:
                show_all.click()
            time.sleep(1)

    def go_to_previous_page(self):
        prev_page = self.driver.find_element(By.XPATH, self.PAGINATION_XPATH)
        if prev_page:
            prev_page.click()
            time.sleep(1)

    def collect_data_through_pagination(self, start_date=None, end_date=None):
        """
        Collect incident reports by incident history pages
        Args:
            start_date: timezone-aware datetime object - start date to collect incidents from
            end_date: timezone-aware datetime object - end date to collect incidents until
        """
        all_incidents_df = pd.DataFrame()
        try:
            self.driver.get(self.provider_url)
            stop_collection = False
            
            while not stop_collection:
                # Show all incidents
                self.show_all_incidents()
                # Get incident record by looping over incidents list in the current page
                incident_df, flag_no_data = self.loop_over_incidents()
                
                # Check if we have incidents and if they're within our date range
                if len(incident_df) > 0:
                    if start_date or end_date:
                        # Make a copy of the Updates column before parsing
                        incident_df['timestamp'] = incident_df['Updates'].apply(
                            lambda x: DataTransformer.parse_update_time(json.loads(x)[0]['Update_Timestamp'])
                        )
                        
                        # Check if we've gone past the start date
                        if start_date and (incident_df['timestamp'].min() < start_date):
                            # Keep only incidents after start_date
                            incident_df = incident_df[incident_df['timestamp'] >= start_date]
                            stop_collection = True
                            print(f"Found incidents before {start_date}, stopping collection.")
                        
                        # Filter end date if specified
                        if end_date:
                            incident_df = incident_df[incident_df['timestamp'] <= end_date]
                    
                    if len(incident_df) > 0:
                        all_incidents_df = pd.concat([all_incidents_df, incident_df])
                
                # Stop if no more pages or we've found older incidents
                if flag_no_data or stop_collection:
                    print("Ending incident collection.")
                    break
                    
                # Go to the previous page
                self.go_to_previous_page()
            
            # Drop the temporary timestamp column used for filtering
            if 'timestamp' in all_incidents_df.columns:
                all_incidents_df = all_incidents_df.drop('timestamp', axis=1)
                
            return all_incidents_df
        except Exception as e:
            print("Executing collect_data_through_pagination(). An error occurred: ", e)
            traceback.print_exc()
            return all_incidents_df





class DataTransformer:
    @staticmethod
    def get_services(service_str):
        if pd.isna(service_str):
            return []
        else:        
            service_str = service_str.split(':')[-1].rstrip('.')
            service_str = service_str.replace("and", ",")
            services = service_str.split(',')
            return [service.strip() for service in services]
    
    @staticmethod    
    def parse_update_time(timestamp_str):
        tzinfos = {
            "PST": gettz("America/Los_Angeles"),
            "PDT": gettz("America/Los_Angeles")
        }
        timestamp_str = " ".join(timestamp_str.split(". ")[1].split(" - "))
        timestamp = parser.parse(timestamp_str, ignoretz=False, tzinfos=tzinfos)
        return timestamp.astimezone(gettz('UTC'))

    @staticmethod
    def parse_updates(updates_list, stages=None):
        if stages is None:
            stages = ["Investigating", "Identified", "Monitoring", "Resolved", "Postmortem"]
        updates_dict = {}
        
        for stage in stages:
            stage = stage.lower()
            updates_dict[f'{stage}_flag'] = int(0)
            updates_dict[f'{stage}_timestamp'] = None
            updates_dict[f'{stage}_description'] = None
        
        for update in updates_list:
            stage = update.get("Update_Title")
            if stage in stages:
                stage = stage.lower()
                updates_dict[f'{stage}_flag'] = int(1)
                updates_dict[f'{stage}_timestamp'] = DataTransformer.parse_update_time(update.get("Update_Timestamp"))
                updates_dict[f'{stage}_description'] = update.get("Update_Body")
        return updates_dict

    @staticmethod
    def get_incident_provider(incident_url):
        if pd.isna(incident_url):
            return incident_url
        else:
            return incident_url.split('/')[2].split('.')[1]

    @staticmethod
    def transform_incidents(df):
        try:
            # Drop duplicates on raw data first
            df = df.drop_duplicates(subset=['Incident_Link'])  # Use Incident_Link as it's unique for each incident
            df = df.reset_index(drop=True)
            
            # Now parse JSON in Updates column
            df = load_json_column(df, 'Updates')

            # Add provider column
            df['provider'] = df['Incident_Link'].apply(DataTransformer.get_incident_provider)
            
            # Get incident id
            df['incident_id'] = df['Incident_Link'].apply(get_incident_id)

            # Numerize incident impact level
            impact_mapping = {
                'impact-none': 0,
                'impact-minor': 1,
                'impact-major': 2,
                'impact-critical': 3,
                'impact-maintenance': 4
            }
            df['incident_impact_level'] = df['Incident_Impact'].map(impact_mapping)

            # Parse services
            df['services'] = df['Service'].apply(DataTransformer.get_services)
            all_services = ['Playground', 'API', 'Labs', 'ChatGPT', 'api.anthropic.com', 
                          'claude.ai', 'console.anthropic.com', 'Character.AI']
            
            for service in all_services:
                df[service] = df['services'].apply(lambda x: 1 if service in x else 0)

            # Parse stages
            df_stages = df.copy()
            df_stages['parsed_updates'] = df_stages['Updates'].apply(DataTransformer.parse_updates)
            df_stages = unnest_dict(df_stages, 'parsed_updates')

            # Calculate time span
            cols_timestamp = [col for col in df_stages.columns if 'timestamp' in col]
            cols_timestamp.pop()  # remove the postmortem timestamp
            df_stages['start_timestamp'] = df_stages[cols_timestamp].min(axis=1)
            df_stages['close_timestamp'] = df_stages[cols_timestamp].max(axis=1)
            df_stages['time_span'] = df_stages['close_timestamp'] - df_stages['start_timestamp']
            df_stages['over_one_day'] = df_stages['time_span'] > timedelta(days=1)

            # Reorder columns
            cols_incident_info = ['incident_id', 'Incident_Title', 'incident_impact_level', 
                                'Incident_color', 'provider']
            cols_services = all_services
            cols_stages = [col for col in df_stages.columns 
                         if 'flag' in col or 'timestamp' in col or 'description' in col]
            cols_timespan = ['time_span', 'over_one_day']

            return df_stages[cols_incident_info + cols_services + cols_stages + cols_timespan]
            
        except Exception as e:
            print(f"Error transforming incidents: {str(e)}")
            traceback.print_exc()
            return None


if __name__ == "__main__":
    MAC_C_KEY = Keys.COMMAND
    # WINDOWS_C_KEY = Keys.CONTROL

    # Define provider URLs
    provider_urls = [
        "https://status.openai.com/history/",
        "https://status.anthropic.com/history",
        "https://status.character.ai/history"
    ]

    # Define date range with timezone
    start_date = datetime(2024, 10, 1, tzinfo=gettz('UTC'))  
    end_date = datetime.now(gettz('UTC'))                  
    
    print(f"Collecting incidents from {start_date} to {end_date}")
    
    all_incidents_df = pd.DataFrame()
    
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("Starting Chrome in headless mode...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Collect data from each provider
        for url in provider_urls:
            print(f"\nCollecting data from: {url}")
            incident_page = MyIncidentPage(driver, url)
            provider_df = incident_page.collect_data_through_pagination(
                start_date=start_date,
                end_date=end_date
            )
            all_incidents_df = pd.concat([all_incidents_df, provider_df])
            print(f"Collected {len(provider_df)} incidents from {url}")

        driver.quit()
        print("\nBrowser session closed.")

        # Step 2: Transform data if we have any incidents
        if len(all_incidents_df) > 0:
            print(f"\nTransforming {len(all_incidents_df)} total incidents...")
            transformed_df = DataTransformer.transform_incidents(all_incidents_df)
            
            if transformed_df is not None:
                # Ensure output directory exists
                os.makedirs('server/static/data', exist_ok=True)
                
                # Write to csv
                output_path = 'server/static/data/incident_stages_all.csv'
                transformed_df.to_csv(output_path, index=False)
                print(f"\nData successfully written to {output_path}")
                print(f"Total incidents processed: {len(transformed_df)}")
            else:
                print("Error: Data transformation failed")
        else:
            print("No incidents were collected")

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        traceback.print_exc()
    finally:
        if 'driver' in locals():
            driver.quit()
            print("Browser session closed.")
