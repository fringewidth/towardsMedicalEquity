# %% [markdown]
# # IV. Scrape Coordinates from Plus Codes
# It is recommended to use the Google Maps API for getting coordinates from Plus Codes. This script is for those who prefer not to use the API.

# This script uses an Edge driver via Selenium to scrape coordinates from Plus Codes.
# The basic principle is to search the plus code, leading Google Maps to jump to the location.
# The URL of the page contains the coordinates of the location.
# The script extracts the coordinates from the URL and saves them to the dataframe.

# %%
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
# %%
df = pd.read_csv("../data/main/2-hospitals_scraped.csv")

# Initialize Latitude and Longitude columns
df['Latitude'] = [None] * len(df)
df['Longitude'] = [None] * len(df)

# %%
def search_plus_code(driver : webdriver.Edge, plusCode: str):
    search_box = driver.find_element(By.ID, 'searchboxinput')
    search_box.clear()
    search_box.send_keys(plusCode)
    search_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, 5).until(EC.url_changes(driver.current_url)) # Wait until Maps jumps to the location and return

# %%
def getCoordinates(plusCode: str, driver: webdriver.Edge) -> tuple[str, str]:
    # Search the plus code
    search_plus_code(driver, plusCode)
    
    # Searching for the Plus Code can either lead to the place/ page of the code, or to the directions to the place.
    # Upon closing the page, we can extract the coordinates from the URL.
    try:
        close_button = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close']"))
        )
    except: # for directions page
        close_button = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close directions']"))
        )
    close_button.click()
    WebDriverWait(driver, 5).until(EC.url_changes(driver.current_url))

    # URL will be in the format https://www.google.com/maps/@lat,lon,[metadata]
    lat, lon = driver.current_url.split('@')[1].split(',')[0:2]
    
    return lat, lon

# %%
edge_driver_path = "E:/Downloads/edgedriver_win64/msedgedriver.exe"
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)

driver.get('https://www.google.com/maps')

with open('error_log_coors.txt', 'w') as f: # Log file for errors
    for i in range(len(df)):
        try:
            if not pd.isna(df['Plus Code'][i]): # Skip if Plus Code is missing
                lat, lon = getCoordinates(df['Plus Code'][i], driver)
                df.at[i, 'Latitude'] = lat
                df.at[i, 'Longitude'] = lon
                print(f'{i}/{len(df)} done. {lat}, {lon}')
            if i % 10 == 0: # Save every 10 iterations
                df.to_csv("hospitals_coordinates.csv", index=False)
        except:
            f.write(f"Error at {i}\n")
            time.sleep(2) # Cautionary wait for the next iteration
            continue
    df.to_csv("../data/main/3-hospitals_scraped_coords.csv", index=False)

driver.quit()
df.to_csv("hospitals_coordinates.csv", index=False) # For the last %10 results.