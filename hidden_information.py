#from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "https://legion-riddle.onrender.com/api/pages"
import requests

def get_all_real_page_urls():
    all_urls = []
    page = 1
    limit = 50
    while True:
        resp = requests.get(BASE_URL, params={"page": page, "limit": limit})
        data = resp.json()
        all_urls.extend([p["url"] for p in data["pages"] if p.get("real_page")])
        if page >= data["pagination"]["totalPages"]:
            break
        page += 1
    return all_urls


def get_hidden_number(url: str) -> int:
    """Go to the page, click all 5 buttons, expand rows, and return the hidden number."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # comment out this line if you want to see the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(url)

        # Click all 5 buttons
        for i in range(5):
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., 'Button {i}')]")))
            btn.click()
            time.sleep(0.3)

        # Expand all collapsible rows
        toggles = driver.find_elements(By.XPATH, "//button[contains(., 'Click to expand')]")
        for t in toggles:
            driver.execute_script("arguments[0].scrollIntoView(true);", t)
            t.click()
            time.sleep(0.3)

        # Extract the number inside span[class^='val']
        number_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class^='val']")))
        hidden_number = int(number_element.text.strip())

        print(f"  → Found number: {hidden_number}")
        return hidden_number

    finally:
        driver.quit()

def main():
    urls = get_all_real_page_urls()
    total_sum = 0



    for url in urls:
        print(f"Visiting {url}")
        num = get_hidden_number(url)
        total_sum += num

  

    print("Total sum:", total_sum)

if __name__ == "__main__":
    main()