from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import json

import os
from dotenv import load_dotenv

from tqdm import tqdm

load_dotenv()

# Paths
EXECUTABLE_PATH = os.environ.get("EXECUTABLE_PATH")
PARENT_DIR = os.environ.get("PARENT_DIR")

# Days of month before
days_month_before = [
    0, # Should be 0 for January
    31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30
]

# Variations list
variations_list = {'S1': 'Sec 1', 'S2': 'Sec 2', 'S3': 'Sec 3', 'S4': 'Sec 4', 'HS': 'Highschool', 'CCA Orientation': 'CCAO', 'Sabbaticals': 'Sabbats', 'Outward Bound Singapore': 'OBS', 'sch': 'School', 'JC2': 'J2', 'JC1': 'J1', 'Biology': 'Bio', 'Physics': 'Phys', 'Chemistry': 'Chem'}

# Function to load cookies
def load_cookies(file):
    with open(file, "r") as r:
        return json.load(r)

# Variations of event title
def variations(event_title):
    result = [event_title,]
    for variation in variations_list:
        new_title = event_title.replace(variation, variations_list[variation])
        if new_title != event_title:
            result.append(new_title)
    return result

# Scrape events, return list
def scrape_events(year):
    # Driver stuff
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(EXECUTABLE_PATH), options=options)
    driver.execute_cdp_cmd("Network.enable", {})
    cookies = load_cookies(PARENT_DIR + "isp_cookies.json") # Read cookies here
    for cookie in cookies:
        cookie["sameSite"] = "None" # Idk what this does but dont delete it
        driver.execute_cdp_cmd("Network.setCookie", cookie)

    events = {}
    for month in tqdm(range(12), desc="Retrieving data for months"):
        # Open calendar for new month
        driver.get(f"https://isphs.hci.edu.sg/eventcalendar.asp?year={year}&month={month + 1}")

        # Find the first day
        first_day = int(driver.find_element(By.XPATH, "//div[@class='fc-day-number']").text)

        # Get event elements
        for event in driver.find_elements(By.XPATH, "//div[contains(@class, 'fc-event fc-event-hori')]"):

            # Get the actual title
            event_title = event.find_element(By.XPATH, ".//span[@class='fc-event-title']").text

            # Get the coordinates of the event
            style = event.get_attribute("style").split(";")
            for property in style:
                property = property.strip(" ").strip("px")
                if property.startswith("left: "):
                    left = int(property.strip("left: "))
                elif property.startswith("width: "):
                    width = int(property.strip("width: "))
                elif property.startswith("top: "):
                    top = int(property.strip("top: "))

            # Get x-index of the event
            x_index = left // 156

            # Get y-index of the event
            y_index = (top - 28) // 133

            # Get number of days of event
            num_days = round(width / 156)

            # Get the adjusted day
            adjusted_day = first_day + x_index + y_index * 7
            real_day = adjusted_day - (days_month_before[month] if first_day != 1 else 0)

            # Preprocess event title into multiple variations
            event_title_variations = variations(event_title)

            # Add to dict
            for event_title in event_title_variations:
                if not event_title in events:
                    events[event_title] = {"day": real_day, "month": month + 1, "num_days": num_days}
                else:
                    events[event_title]["num_days"] += num_days
                    if 0 < real_day < events[event_title]["day"] and (month + 1) <= events[event_title]["month"]:
                        events[event_title]["day"] = real_day
                        events[event_title]["month"] = month + 1
    
    return events

if __name__ == "__main__":
    events = scrape_events(2023)
    print(events)
    with open(PARENT_DIR + "src/data/isp_events.json", "w") as file:
        json.dump(events, file, indent=4)