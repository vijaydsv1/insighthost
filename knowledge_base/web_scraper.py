import requests
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_page_content(url):

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)

        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")

        text = "\n".join(
            p.get_text(strip=True)
            for p in paragraphs
            if len(p.get_text(strip=True)) > 40
        )

        return text[:6000]

    except Exception:
        print("Failed:", url)
        return ""


def scrape_services():

    print("Loading service structure...")

    with open("knowledge_base/scraped_data.json") as f:
        services = json.load(f)

    visited = set()
    data = []

    for item in services:

        url = item["source"]

        if url in visited:
            continue

        visited.add(url)

        print("Scraping:", item["service"])

        content = get_page_content(url)

        data.append({
            "category": item["category"],
            "pillar": item["pillar"],
            "service": item["service"],
            "content": content,
            "source": url
        })

        time.sleep(1)

    with open("knowledge_base/services_full.json", "w") as f:
        json.dump(data, f, indent=2)

    print("\nScraping finished")
    print("Total services scraped:", len(data))


if __name__ == "__main__":
    scrape_services()