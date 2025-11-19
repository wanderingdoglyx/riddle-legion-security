import asyncio
import pyppeteer
import requests
import re

BASE_URL = "https://legion-riddle.onrender.com/api/pages"

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

async def collect_hidden_number(page):
    # 1️⃣ Click all buttons
    buttons = await page.querySelectorAll("button")
    for i, button in enumerate(buttons[:10]):
        try:
            await button.click()
        except Exception:
            print(f"Could not click button {i}")

    # 2️⃣ Wait for table
    try:
        await page.waitForSelector("table#important-information", timeout=5000)
        
        # 3️⃣ Click all rows
        rows = await page.querySelectorAll("table#important-information tr")
        for row in rows:
            try:
                await row.click()
            except Exception:
                pass

        # 4️⃣ Extract numbers
        number_text = await page.evaluate('''() => {
            const table = document.querySelector("table#important-information");
            return table ? table.textContent : '';
        }''')
        
        numbers = [int(n) for n in re.findall(r"\b\d+\b", number_text)]
        return sum(numbers)
    except Exception as e:
        print(f"Table error: {e}")
        return 0

async def main():
    urls = get_all_real_page_urls()
    total_sum = 0

    browser = await pyppeteer.launch(headless=True)
    page = await browser.newPage()

    for url in urls:
        print(f"Visiting {url}")
        try:
            await page.goto(url, waitUntil='networkidle0')
            total_sum += await collect_hidden_number(page)
        except Exception as e:
            print(f"Error: {e}")
            continue

    await browser.close()
    print("Total sum:", total_sum)

if __name__ == "__main__":
    asyncio.run(main())