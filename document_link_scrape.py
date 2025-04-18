from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import json, random, time

options = Options()
options.add_argument("--headless=new")  # new headless mode
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)

# Stealth mode
stealth(driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)


base_url = "https://luatvietnam.vn/van-ban/tim-van-ban.html"
doc_base_url = "https://luatvietnam.vn"

def scrape_page(page_number):
    url = f"{base_url}?keywords=&SearchOptions=1&SearchByDate=issueDate&DateFromString=&DateToString=&DocTypeIds=10&OrganIds=0&FieldIds=0&LanguageId=0&SignerIds=0&RowAmount=20&PageIndex={page_number}"
    driver.get(url)
    time.sleep(3)  # Wait for JavaScript to load content

    soup = BeautifulSoup(driver.page_source, "html.parser")

    titles = soup.find_all("h2", class_="doc-title")
    download_links =  soup.select('a.doc-tag2[title="Tải về"]')
    metadata_doc = soup.select("div.post-meta-doc")
    data = []
    for title, link, meta in zip(titles, download_links, metadata_doc):
        issue_date = meta.select_one("div.doc-dmy span.w-doc-dmy2")
        data.append({
            "title": title.get_text(strip=True),
            "link": doc_base_url + link["href"],
            "issue_date": issue_date.get_text(strip=True) if issue_date else None
        })
    return data
    
    # for t, lk in zip(titles, download_links):
    #     print(f"Title: {t}\n Link: {lk}\n")

# Crawl multiple pages and assign unique IDs
all_documents = []
doc_id = 1
total_pages =  38 # Set this to the total number of pages you want to scrape

for page in range(1, total_pages + 1):
    print(f"Scraping page {page}...")
    page_data = scrape_page(page)
    print(f"Got {len(page_data)} documents from page {page}")
    for doc in page_data:
        doc["id"] = doc_id
        doc_id += 1
        all_documents.append(doc)
    # Randomize delay between page requests
    time.sleep(random.uniform(2, 5))

# Save to JSON file
with open("document_links.json", "w", encoding="utf-8") as f:
    f.write("")
    json.dump(all_documents, f, ensure_ascii=False, indent=2)

driver.quit()
print("Scraping complete. Saved to document_links.json.")
