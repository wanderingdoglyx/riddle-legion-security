import requests
from bs4 import BeautifulSoup
import re
from playwright.sync_api import sync_playwright

BASE_URL = "https://legion-riddle.onrender.com/"  # Change if needed
OPENAPI_URL = f"{BASE_URL}/api/pages"

# Step 1: Get list of real pages
response = requests.get(OPENAPI_URL)
data = response.json()

total = 0
count = 0

for page in data.get("pages", []):
    url = BASE_URL + page["url"]
    print(f"Fetching {url}...")

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    # Find the "Important Information Table"
    table = soup.find("table", string=re.compile("Important Information Table", re.I))
    if not table:
        continue
    table = table.find_parent("table")

    # Extract number from the table (could be in any cell)
    text = table.get_text()
    numbers = re.findall(r'\b\d+\b', text)
    if numbers:
        num = int(numbers[0])  # or logic to pick the right one
        total += num
        count += 1
        print(f"Found: {num} | Total: {total}")

print(f"\nCollected {count} numbers.")
print(f"Final Sum: {total}")