# %% [markdown]
# # II. Extract hospital data from Google Maps
# We use an Edge Driver via Selenium to scrape the ratings, number of reviews, and Plus Code of each hospital in the dataset.
# The dataset is split into multiple CSV files to be processed in parallel.
# The extracted data is saved in a new CSV file. 
# *Few Kinks*:
# 1. The Plus Code is not always available for all hospitals. In which case, the cell will be empty.
# 2. If searching for the hospitals extracted from the pdf does not directly redirect to the hospital's Google Maps page, the script will click on the first search result. We note that this is not always accurate, however it is the best we can do without manual intervention.
# 3. Sometimes, the first result will be an ad. Although we have observed that this is rare when searching for healthcare, and therefore we have not implemented a check for this.
# 4. The script will save the data every 10 hospitals to prevent data loss in case of an error.

# *Note*: We do not condone the use of scraping tools for commercial purposes. This script was created to identify areas in India that are underserved by healthcare facilities. Please read the Google Maps Terms of Service before using this script.
# We take no responsibility for the misuse of this script.
# %%
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# %%
# Each individual scraper is assigned a csvIndex, which they need to update here as well as the filename of the hospitals csv file.
# UPDATE THIS
csvIndex = 3
edge_driver_path = "E:/Downloads/edgedriver_win64/msedgedriver.exe"

# %%

# Load the dataset and remove unnecessary columns
hospitals = pd.read_csv(f'../data/temp/hospitals-pdf_{csvIndex}.csv')
hospitals.drop(columns=['PPN / NON PPN', 'Address'], inplace=True)

# %%
# Initialize the columns for the extracted data
hospitals['Rating'] = [None] * len(hospitals)
hospitals['Number of Reviews'] = [None] * len(hospitals)
hospitals['Plus Code'] = [None] * len(hospitals)

# %%
# Concatenates the name of the hospital, the residing city and its corresponding state.
# This usually leads directly to the hospital's Google Maps page.
def getSearchTerm(rowIndex):
    print("Generating full address for row", rowIndex)
    return ', '.join(hospitals.iloc[rowIndex].dropna()).replace('\n', '').replace('\r', '')

# %%
# Searches for the address in Google Maps
def search(address, driver):
    search_box = driver.find_element(By.ID, 'searchboxinput')
    search_box.clear() 
    search_box.send_keys(address)
    search_box.send_keys(Keys.RETURN)         

# %%
"""
<!-- TARGET HTML STRUCTURE -->
<div class="F7nice " jslog="76333;mutable:true;">
    <span>
        <span aria-hidden="true">4.8</span>
        <span class="ceNzKf" role="img" aria-label="4.8 stars ">
            <span class="rFrJzc"></span>
            <span class="rFrJzc"></span>
            <span class="rFrJzc"></span>
            <span class="rFrJzc"></span>
            <span class="rFrJzc"></span>
        </span>
    </span>
    <span>
        <span>
            <span aria-label="1,168 reviews">(1,168)</span>
        </span>
    </span>
</div>
"""

# Scrapes the rating, number of reviews, and Plus Code of the hospital. Works only when the browser is on a search page or a place page.
def scrape_data(driver):
    # Artificial bottleneck
    time.sleep(2)
    
    # If the search did not redirect to the hospital's Google Maps page, click on the first search result
    if driver.current_url.startswith("https://www.google.com/maps/search/"):
        try:
            print("Initial search did not redirect to hospital page. Clicking on first search result.")
            WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.hfpxzc")) # a.hfpxzc is the class of a result. By default, the first result is clicked.
            ).click()
        except Exception as e:
            print("No search results found:", e)
            return None, None, None


    def get_element_text(selector, attribute=None):
        try:
            element = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.get_attribute(attribute) if attribute else element.text
        except Exception as e:
            print(f"Error scraping {selector}:", e)
            return None

    rating = get_element_text("div.F7nice span[aria-hidden='true']")
    num_reviews = get_element_text("div.F7nice span > span > span[aria-label]", "aria-label")
    if num_reviews:
        num_reviews = int(num_reviews.strip('()').replace(',', '').split(' ')[0]) # Reviews are in the format "(1,168)"
    plus_code = get_element_text("button.CsEnBe[aria-label*='Plus code: ']", "aria-label")
    if plus_code:
        plus_code = plus_code.split(': ')[1] # Plus code is in the format "Plus code: 1234+56"
    
    print("Scraped data:", rating, num_reviews, plus_code)
    return rating, num_reviews, plus_code




# %%
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)

driver.get('https://www.google.com/maps')
with open(f"error_log{csvIndex}.txt", "w") as f: # Log file for errors
    for i in range(len(hospitals)):
        try:
            print(f"Processing row {i}")
            address = getSearchTerm(i)
            search(address, driver)

            rating, num_reviews, plus_code = scrape_data(driver)

            # Update the dataset
            hospitals.at[i, 'Rating'] = rating
            hospitals.at[i, 'Number of Reviews'] = num_reviews
            hospitals.at[i, 'Plus Code'] = plus_code

            try:
                close_button = WebDriverWait(driver, 4).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close']"))
                )
            except: # Sometimes searching for a hospital opens up Navigation. don't bother scraping data in this case, and simply close once WebDriver times out.
                close_button = WebDriverWait(driver, 4).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close directions']"))
                )
            close_button.click()

            if i % 10 == 0: # Save the data every 10 hospitals
                hospitals.to_csv(f'../data/temp/hospitals_{csvIndex}_ratings.csv', index=False)

        except Exception as e:
            f.write(f"Error at index {i}: {str(e)}\n")
            f.flush() # Write to file immediately
            continue
hospitals.to_csv(f'hospitals_{csvIndex}_ratings.csv', index=False) # For the last %10 hospitals

driver.quit()


