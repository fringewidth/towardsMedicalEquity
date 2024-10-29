# %%
import pandas as pd
df = pd.read_csv("hospitals_ratings.csv")
df['Latitude'] = [None] * len(df)
df['Longitude'] = [None] * len(df)

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
def search_location(driver : webdriver.Edge, plusCode: str):
    search_box = driver.find_element(By.ID, 'searchboxinput')
    search_box.clear()
    search_box.send_keys(plusCode)
    search_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, 5).until(EC.url_changes(driver.current_url))

# %%
def getCoordinates(plusCode: str, driver: webdriver.Edge) -> tuple[str, str]:
    search_location(driver, plusCode)
    try:
        close_button = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close']"))
        )
    except:
        close_button = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close directions']"))
        )
    close_button.click()
    WebDriverWait(driver, 5).until(EC.url_changes(driver.current_url))

    lat, lon = driver.current_url.split('@')[1].split(',')[0:2]
    
    return lat, lon

# %%
edge_driver_path = "E:/Downloads/edgedriver_win64/msedgedriver.exe"
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)

driver.get('https://www.google.com/maps')
# time.sleep(5)
with open('error_log_coors.txt', 'w') as f:
    for i in range(2550, len(df)):
        try:
            if not pd.isna(df['Plus Code'][i]):
                lat, lon = getCoordinates(df['Plus Code'][i], driver)
                df.at[i, 'Latitude'] = lat
                df.at[i, 'Longitude'] = lon
                print(f'{i}/{len(df)} done. {lat}, {lon}')
            if i % 10 == 0:
                df.to_csv("hospitals_coordinates.csv", index=False)
        except:
            f.write(f"Error at {i}\n")
            time.sleep(2)
            continue
    df.to_csv("hospitals_coordinates.csv", index=False)



