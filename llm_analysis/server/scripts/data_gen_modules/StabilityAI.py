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
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.color import Color


def calculate_start_date(end_date):
    start_date = end_date - relativedelta(months=2)
    start_date_str = start_date.strftime("%Y%m")
    end_date_str = end_date.strftime("%Y%m")
    return start_date_str, end_date_str


# Helper function to construct archive paths
def get_archive_path(partition):
    # Use relative path from the current file's location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    archive_folder = os.path.join(current_dir, "static/data")

    start_date, end_date = calculate_start_date(partition)
    os.makedirs(archive_folder, exist_ok=True)
    file_path = os.path.join(archive_folder, f"incident_history_{start_date}_{end_date}.csv")
    return file_path


class MyIncidentPage:
    # Class-specific XPath constants
    UPDATE_XPATH = "//div[contains(@class, 'incident-update')]"
    SERVICE_XPATH = "//div[contains(@class, 'item__affected-components')]"
    INCIDENT_LIST_XPATH = "//a[contains(@class, 'incident-details')]"
    PAGE_XPATH = "//h3[contains(@class, 'incidents-monthly__item__month')]"
    PAGINATION_XPATH = "//div[@class='pagination']//i[contains(@class, 'flex items-center')]"
    SHOW_ALL_XPATH = "//div[contains(@class, 'expand-incidents') and @aria-expanded='false']"

    def __init__(self, driver):
        self.driver = driver
        self.c_key = MAC_C_KEY

    def get_incident_updates(self):
        try:
            update_rows = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, self.UPDATE_XPATH))
            )
            updates = []
            for update_row in update_rows:
                try:
                    title = update_row.find_element(By.XPATH, ".//div[contains(@class, 'update-title')]").text
                    body = update_row.find_element(By.XPATH, ".//div[contains(@class, 'update-body')]").text
                    timestamp = update_row.find_element(By.XPATH, ".//div[contains(@class, 'update-timestamp')]").text
                    updates.append({
                        "Update_Title": title,
                        "Update_Body": body,
                        "Update_Timestamp": timestamp,
                    })
                except NoSuchElementException:
                    print("An element within the update row was missing.")
            return json.dumps(updates)
        except TimeoutException:
            print("No updates found for this incident.")
            return json.dumps([])

    # Method to collect service information
    def get_incident_service(self):
        try:
            service_text = self.driver.find_element(By.XPATH, self.SERVICE_XPATH).text
            service = service_text.split("\n")[0] if service_text else "No affected services found."
        except NoSuchElementException:
            service = "No affected services found."
        return service

    def switch_to_incident(self, incident, original_window):
        print("Switching to new window:")
        try:
            title_full_text = incident.text.strip()
            title = title_full_text.split("\n")[0] if title_full_text else "No Title"
            link = incident.get_attribute('href')
            print(f"Processing StabilityAI link: {link}")
            updates = title_full_text.split("\n")[1:]  # Everything except the first line
            updates = json.dumps({"Details": " ".join(updates)}) if updates else "No details available"
            impact = "impact-minor" if "minor" in incident.get_attribute('class') else "impact-critical"  # Adjust as per the class attributes
            try:
                incident_color = Color.from_string(incident.value_of_css_property('color')).hex
            except Exception:
                incident_color = "#000000"  # Default to black if color not found

            # Open in new tab
            incident.send_keys(self.c_key + Keys.RETURN)
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            new_window = [window for window in self.driver.window_handles if window != original_window][0]
            self.driver.switch_to.window(new_window)

            updates = self.get_incident_updates()
            print(f"Updates collected for {title}: {updates}")
            service = self.get_incident_service()

            # Adjust the service format to match the requirement
            if service:
                service = f"This incident affected: {service}"

            record = pd.DataFrame({
                "Incident_Title": [title],
                "Incident_Link": [link],
                "Incident_color": [incident_color],
                "Incident_Impact": [impact],
                "Updates": [updates],
                "Service": [service],
            })

            print(f"Processed incident: {title}")
            self.driver.close()
            self.driver.switch_to.window(original_window)
            return record
        except Exception as e:
            print(f"Error processing incident: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    # Get a list of all incidents on the page
    def get_incident_list(self):
        try:
            incidents = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, self.INCIDENT_LIST_XPATH))
            )
            return incidents
        except TimeoutException:
            print("No incidents found on this page.")
            return []

    # Archive incidents into a CSV file
    def archive_incidents(self, incident_df):
        date_str = self.driver.find_element(By.XPATH, self.PAGE_XPATH).text
        try:
            date_partition = datetime.strptime(date_str, "%b %Y")
            file_path = get_archive_path(date_partition)

            if not incident_df.empty:
                incident_df.to_csv(file_path, index=False)
                print(f"File saved successfully at: {file_path}")
            else:
                print("No data to save. DataFrame is empty.")
        except Exception as e:
            print(f"Error saving file: {e}")
            traceback.print_exc()

    # Navigate to the previous page
    def go_to_previous_page(self):
        try:
            prev_page = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.PAGINATION_XPATH))
            )
            prev_page.click()
            time.sleep(2)
        except TimeoutException:
            return False
        return True

    # Collect incident data with pagination
    def collect_data_through_pagination(self):
        while True:
            self.show_all_incidents()
            incident_list = self.get_incident_list()
            if not incident_list:
                print("No incidents found. Ending collection.")
                break

            incident_df = pd.DataFrame()
            original_window = self.driver.current_window_handle

            for incident in incident_list:
                record = self.switch_to_incident(incident, original_window)
                incident_df = pd.concat([incident_df, record])

            if not incident_df.empty:
                self.archive_incidents(incident_df)

            if not self.go_to_previous_page():
                break

    # Expand all incidents on the page
    def show_all_incidents(self):
        try:
            show_all_buttons = self.driver.find_elements(By.XPATH, self.SHOW_ALL_XPATH)
            for button in show_all_buttons:
                button.click()
            time.sleep(2)
        except Exception as e:
            print("Error clicking 'Show All' button:", e)


if __name__ == "__main__":
    MAC_C_KEY = Keys.COMMAND
    
    # Configure Chrome options for headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Initialize driver with options
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://stabilityai.instatus.com/history/1")
    try:
        incident_page = MyIncidentPage(driver)
        incident_page.collect_data_through_pagination()
    finally:
        driver.quit()
