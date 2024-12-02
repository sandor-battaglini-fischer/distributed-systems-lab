import re
import time
import os
import traceback
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.color import Color


def calculate_start_date(end_date):
    start_date = end_date - relativedelta(months=2)
    start_date_str = start_date.strftime("%Y%m")
    end_date_str = end_date.strftime("%Y%m")
    return start_date_str, end_date_str

def rgba_to_hex(rgba):
        match = re.match(r'rgba\((\d+), (\d+), (\d+), (\d+(\.\d+)?)\)', rgba)
        if match:
            r = int(match.group(1))
            g = int(match.group(2))
            b = int(match.group(3))
            return "#{:02x}{:02x}{:02x}".format(r, g, b)
        else:
            return rgba
def determine_service_type(update_title, update_body):
    text_to_check = f"{update_title} {update_body}".lower()
    if "rest" in text_to_check:
        return "REST API"
    elif "grpc" in text_to_check:
        return "gRPC API"
    elif "stable" in text_to_check or "assistant" in text_to_check:
        return "Stable Assistant"
    else:
        return "Unknown Service"

def get_archive_path(partition):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Gets the server directory
    start_date, end_date = calculate_start_date(partition)
    archive_folder = os.path.join(BASE_DIR, "static/data/raw/incident/stabilityAI")
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
    SHOW_ALL_XPATH = "//div[contains(@class, 'relative') and contains(@class, 'incidents-monthly__item')]//button[contains(text(), 'Load more')]"

    def __init__(self, driver):
        self.driver = driver
        self.c_key = MAC_C_KEY

    def get_incident_updates(self):
        try:
            update_rows = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'incident-update')]"))
            )
            updates = []
            for update_row in update_rows:
                try:
                    status_elements = update_row.find_elements(By.XPATH, ".//div[contains(@class, 'update-list-item__status')]")
                    print(f"Found {len(status_elements)} status elements.")

                    if status_elements:
                        # Take the first non-empty status (either mobile or desktop)
                        title = None
                        for status in status_elements:
                            if status.text.strip():
                                title = status.text.strip()
                                break
                        #print(f"Extracted Title: {title}")
                    else:
                        #print("Status element not found.")
                        title = None

                    # Adjust the XPath for body extraction
                    try:
                        body_elements = update_row.find_elements(By.XPATH,".//div[contains(@class, 'prose-sm') and contains(@class, 'prose')]//p | .//div[contains(@class, 'prose-sm') and contains(@class, 'prose')]")
                        if body_elements:
                            body = body_elements[0].text.strip()  # Grab the first body element
                            #print(f"Extracted Body: {body}")
                        else:
                            #print("No body elements found.")
                            body = None
                    except NoSuchElementException:
                        #print("Body element not found.")
                        body = None

                    # Extract the timestamp
                    try:
                        timestamp = update_row.find_element(By.XPATH, ".//time").get_attribute("datetime")
                        #print(f"Extracted Timestamp: {timestamp}")
                    except NoSuchElementException:
                        #print("Timestamp element not found.")
                        timestamp = None

                    updates.append({
                        "Update_Title": title,
                        "Update_Body": body,
                        "Update_Timestamp": timestamp,
                    })
                except NoSuchElementException:
                    print("An element within the update row was missing.")
            return json.dumps(updates)
        except TimeoutException:
            #print("No updates found for this incident.")
            return json.dumps([])

    def get_incident_service(self, update_title, update_body, incident_title, updates):
        text_to_check = f"{update_title} {update_body} {incident_title}".lower().strip()

        for update in updates:
            update_title = update.get("Update_Title", "").lower().strip()  # Make sure to check title and body of each update
            update_body = update.get("Update_Body", "").lower().strip()

            text_to_check += f" {update_title} {update_body}"

        #print("Text to check after updates:", text_to_check)

        rest_api_found = "rest" in text_to_check
        grpc_api_found = "grpc" in text_to_check
        api_found = "api" in text_to_check
        latency_found = "latency" in text_to_check
        error_found = "error" in text_to_check
        stable_found = "stable" in text_to_check or "assistant" in text_to_check

        # checking flags for debugging purposes
        # print(f"REST API found: {rest_api_found}, gRPC API found: {grpc_api_found}, API found: {api_found}, Latency found: {latency_found}, Error found: {error_found}, Stable found: {stable_found}")

        if rest_api_found and grpc_api_found:
            return "REST API and gRPC API"
        elif rest_api_found:
            return "REST API"
        elif grpc_api_found:
            return "gRPC API"
        elif api_found:
            return "REST API and gRPC API"
        elif stable_found:
            return "Stable Assistant"
        # Check for "latency" or "error", but neither "REST", "gRPC", "API", nor "Stable" is found
        elif (latency_found or error_found) and not (rest_api_found or grpc_api_found or api_found or stable_found):
            return "REST API and gRPC API"
        else:
            return "Unknown Service"

    def switch_to_incident(self, incident, original_window):
        print("Switching to new window:")
        try:
            title_full_text = incident.text.strip()
            title = title_full_text.split("\n")[0] if title_full_text else "No Title"
            link = incident.get_attribute('href')
            #print(f"Processing StabilityAI link: {link}")

            updates = title_full_text.split("\n")[1:]  # Everything except the first line
            updates = json.dumps({"Details": " ".join(updates)}) if updates else "No details available"

            incident.send_keys(self.c_key + Keys.RETURN)
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            new_window = [window for window in self.driver.window_handles if window != original_window][0]
            self.driver.switch_to.window(new_window)

            from selenium.common.exceptions import StaleElementReferenceException

            try:
                impact_element = driver.find_element( By.XPATH,"//div[contains(@class, 'incident-details__affected-components-item')]//div[contains(@class, 'bg-disrupted') or contains(@class, 'bg-degraded') or contains(@class, 'bg-down') or contains(@class, 'bg-ok')]/following-sibling::span").text
                impact_content = impact_element
                color_element = driver.find_element(By.XPATH, "//div[contains(@class, 'incident-details__affected-components-item')]//div[contains(@class, 'bg-disrupted') or contains(@class, 'bg-degraded') or contains(@class, 'bg-down') or contains(@class, 'bg-ok')]")
                background_color = color_element.value_of_css_property('background-color')
                print(f"Impact Content: {impact_content}")
                hex_color = rgba_to_hex(background_color)
                #print(f"Impact Color: {hex_color}")
            except StaleElementReferenceException:
                impact_element = driver.find_element(By.XPATH, "//div[contains(@class, 'incident-details__affected-components-item')]//div[contains(@class, 'bg-disrupted') or contains(@class, 'bg-degraded') or contains(@class, 'bg-down') or contains(@class, 'bg-ok')]/following-sibling::span").text
                impact_content = impact_element
                color_element = driver.find_element(By.XPATH,"//div[contains(@class, 'incident-details__affected-components-item')]//div[contains(@class, 'bg-disrupted') or contains(@class, 'bg-degraded') or contains(@class, 'bg-down') or contains(@class, 'bg-ok')]")
                background_color = color_element.value_of_css_property('background-color')
                #print(f"Impact Content: {impact_content}")

                hex_color = rgba_to_hex(background_color)
                #print(f"Impact Color: {hex_color}")

            update_data = self.get_incident_updates()
            #print(f"Updates collected for {title}: {update_data}")

            # Parse the JSON string into a list
            updates = json.loads(update_data)

            # make sure the updates is a list before accessing
            if isinstance(updates, list) and updates:
                # Extract the title and body from the first update
                update_title = updates[0].get("Update_Title", "")
                update_body = updates[0].get("Update_Body", "")

                service = self.get_incident_service(update_title, update_body, title, updates)
            else:
                service = "Unknown Service"

            # checking the collected service
            #print(f"Service: {service}")

            incident_impact_mapping = {
                "Operational": 0,
                "Degraded performance": 1,
                "Partial outage": 2,
                "Major outage": 4
            }

            incident_impact_value = incident_impact_mapping.get(impact_content, -1)
            #print(f"Mapped Incident Impact Value: {incident_impact_value}")

            record = pd.DataFrame({
                "Incident_Title": [title],
                "Incident_Link": [link],
                "Incident_color": [hex_color],
                "Incident_Impact": [incident_impact_value],
                "Updates": [updates],
                "Service": [f"This incident affected: {service}"],
            })

            #print(f"Processed incident: {title}")
            self.driver.close()
            self.driver.switch_to.window(original_window)
            return record
        except Exception as e:
            #print(f"Error processing incident: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_incident_list(self):
        try:
            incidents = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_all_elements_located((By.XPATH, self.INCIDENT_LIST_XPATH))
            )

            # Check if incidents were found
            if incidents:
                print(f"Incidents found on the page: {len(incidents)}")
            else:
                print("No incidents found.")

            return incidents if incidents else []  # Return an empty list if no incidents found
        except TimeoutException:
            print("Error fetching incident list: Timeout - No incidents found on the page.")
            return []  # Return an empty list if no incidents found
        except Exception as e:
            print(f"Error fetching incident list: {e}")
            return []

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
                if isinstance(incident_list, bool):
                    flag_no_data = True
                else:
                    # looping over incidents when there are any
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

    def archive_incidents(self, incident_df):
        try:
            date_str = self.driver.find_element(By.XPATH, self.PAGE_XPATH).text
            date_partition = datetime.strptime(date_str, "%b %Y")
            file_path = get_archive_path(date_partition)

            if not incident_df.empty:
                incident_df.to_csv(file_path, index=False)
                print(f"Data for {date_str} saved successfully at: {file_path}")
            else:
                print(f"No data collected for {date_str}. Skipping file save.")
        except Exception as e:
            print(f"Error saving data for the current page: {e}")
            traceback.print_exc()

    def show_all_incidents(self):
        try:
            #print("Starting to load all incidents...")
            while True:
                try:
                    #print(f"Checking for 'Load More' button using XPath: {self.SHOW_ALL_XPATH}")
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, self.SHOW_ALL_XPATH))
                    )
                except TimeoutException:
                    #print("Timed out waiting for 'Load More' button. Assuming no more data to load.")
                    break
                buttons = self.driver.find_elements(By.XPATH, self.SHOW_ALL_XPATH)
                if not buttons:
                    #print("No 'Load More' buttons found.")
                    break

                show_all_buttons = self.driver.find_elements(By.XPATH, self.SHOW_ALL_XPATH)
                if show_all_buttons:
                    print(f"Found {len(show_all_buttons)} 'Load More' buttons.")
                else:
                    print("No 'Load More' buttons found.")
                    break  # Exit if no buttons are found
                button = buttons[0]

                for show_all_button in show_all_buttons:
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_all_button)
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, self.SHOW_ALL_XPATH))
                        )
                        self.driver.execute_script("arguments[0].click();", button)
                        #print("Clicked 'Load More' button.")
                        time.sleep(5)  # Wait for content to load

                    except StaleElementReferenceException:
                        print("Stale element encountered. Retrying...")
                        continue

        except Exception as e:
            print(f"Error in 'show_all_incidents': {e}")
            traceback.print_exc()

    def go_to_previous_page(self):
        try:
            prev_page = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Previous page']"))
            )
            href = prev_page.get_attribute("href")
            if href:
                print(f"Navigating to the previous page: {href}")
                prev_page.click()  # Click the button to go to the previous page
                time.sleep(2)  # Allow the page to load
                return True
            else:
                #print("Previous page button is disabled or lacks a valid link.")
                return False
        except TimeoutException:
                #print("Previous page button not found. Ending navigation.")
                return False
        except Exception as e:
            #print(f"Error during navigation to the previous page: {e}")
            traceback.print_exc()
            return False

    # Collect incident data with pagination
    def collect_data_through_pagination(self):
        try:
            while True:

                self.show_all_incidents()

                incident_list = self.get_incident_list()

                if not incident_list:  # handle both None or empty list cases
                    print("No incidents found. Ending collection.")
                    break  # Break out of the loop if no incidents

                incident_df = pd.DataFrame()  # Initialize an empty DataFrame for incidents
                original_window = self.driver.current_window_handle

                for incident in incident_list:
                    record = self.switch_to_incident(incident, original_window)
                    incident_df = pd.concat([incident_df, record],  ignore_index=True)  # Concatenate new record to DataFrame

                # Archive the collected data if the DataFrame is not empty
                if not incident_df.empty:
                    self.archive_incidents(incident_df)
                else:
                    print("No data collected on this page.")

                # Try to navigate to the next page or check for the previous page
                if not self.go_to_previous_page():
                    print("No more pages to navigate. Ending incident collection.")
                    break  # End collection if no more pages are available

        except Exception as e:
            print("Error during pagination:", e)
            traceback.print_exc()

if __name__ == "__main__":
    MAC_C_KEY = Keys.COMMAND  # For macOS, replace with Keys.CONTROL on Windows

    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--window-size=1920x1080")  # Set window size for compatibility
    chrome_options.add_argument("--no-sandbox")  # Required for some environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Handle shared memory issues in Docker

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://stabilityai.instatus.com/history/1")
    try:
        incident_page = MyIncidentPage(driver)
        incident_page.collect_data_through_pagination()
    finally:
        driver.quit()
