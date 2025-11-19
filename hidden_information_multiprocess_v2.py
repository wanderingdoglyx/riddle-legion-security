from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ProcessPoolExecutor, as_completed
import requests
import time
import os

BASE_URL = "https://legion-riddle.onrender.com/api/pages"
OUTPUT_FILE = "results.txt"


def get_all_real_page_urls():
    """Fetch all page URLs from the API that have real_page=True."""
    all_urls = []
    page = 1
    limit = 50
    while True:
        resp = requests.get(BASE_URL, params={"page": page, "limit": limit}, timeout=10)
        data = resp.json()
        all_urls.extend([p["url"] for p in data["pages"] if p.get("real_page")])
        if page >= data["pagination"]["totalPages"]:
            break
        page += 1
    return all_urls


def get_hidden_number(url: str) -> tuple[str, int]:
    """Open a page, click buttons, expand rows, and return (url, hidden_number)."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")   # comment this line to see the browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # If network blocked, replace ChromeDriverManager().install() with your local chromedriver path
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
        print(f"[{os.getpid()}] {url} → {hidden_number}")
        return url, hidden_number

    except Exception as e:
        print(f"[{os.getpid()}] Error with {url}: {e}")
        return url, 0

    finally:
        driver.quit()


def main():
    urls = get_all_real_page_urls()
    print(f"Found {len(urls)} real URLs")

    total_sum = 0
    start_time = time.time()

    # Clean output file before writing
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("URL\tHiddenNumber\n")

    # Limit number of parallel Chrome processes (Chrome is memory-heavy)
    max_workers = min(4, os.cpu_count() or 2)
    print(f"Running with {max_workers} parallel workers...\n")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(get_hidden_number, url): url for url in urls}

        for future in as_completed(futures):
            url, result = future.result()
            total_sum += result
            # Append each result to the output file
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{url}\t{result}\n")

    elapsed = time.time() - start_time
    print(f"\n✅ Total sum: {total_sum}")
    print(f"📝 Results saved to {OUTPUT_FILE}")
    print(f"⏱ Completed in {elapsed:.2f} seconds using {max_workers} processes")


if __name__ == "__main__":
    main()
