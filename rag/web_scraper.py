import time
import urllib.robotparser
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from langchain_core.documents import Document


# =========================================================
# Web Scraper: Accion Labs Site -> Documents
# =========================================================
# Uses the site's own sitemap.xml as the URL source rather
# than following links page-by-page - it's the authoritative,
# complete list of indexable pages the site itself publishes,
# so it avoids both the fragility of link-crawling (infinite
# loops, off-site drift) and the need to guess at site
# structure. robots.txt is still honored per-URL as a second
# check, since a sitemap entry isn't a guarantee of crawl
# permission.

SITE_ROOT = "https://www.accionlabs.com"

SITEMAP_URL = f"{SITE_ROOT}/sitemap.xml"

USER_AGENT = "InsightHostBot/1.0 (+internal knowledge base ingestion)"

REQUEST_TIMEOUT_SECONDS = 15

REQUEST_DELAY_SECONDS = 0.5

# None = every URL in the sitemap (after robots.txt filtering).
# Set an integer while testing to keep a run short.
DEFAULT_MAX_PAGES = None

SITEMAP_XML_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


# =========================================================
# Robots.txt
# =========================================================
_robot_parser = None


def _get_robot_parser():

    global _robot_parser

    if _robot_parser is None:

        _robot_parser = urllib.robotparser.RobotFileParser()

        _robot_parser.set_url(f"{SITE_ROOT}/robots.txt")

        try:

            _robot_parser.read()

        except Exception as e:

            print(f"Could not read robots.txt, proceeding cautiously: {e}")

    return _robot_parser


def is_allowed(url):

    try:

        return _get_robot_parser().can_fetch(USER_AGENT, url)

    except Exception:

        # If robots.txt can't be evaluated, err on the side of
        # not scraping rather than assuming permission.
        return False


# =========================================================
# Sitemap
# =========================================================
def fetch_sitemap_urls(sitemap_url=SITEMAP_URL):

    response = requests.get(
        sitemap_url,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT_SECONDS
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    urls = [

        loc.text.strip()

        for loc in root.findall("sm:url/sm:loc", SITEMAP_XML_NS)

        if loc.text
    ]

    # Only pages actually on this site's own domain.
    urls = [

        u for u in urls

        if urlparse(u).netloc == urlparse(SITE_ROOT).netloc
    ]

    return urls


# =========================================================
# Page Scraping
# =========================================================
def scrape_page(url):

    """
    Fetch one page and extract its title, meta description,
    and main visible text. Returns None on any failure so a
    single bad page can't stop the batch.
    """

    try:

        response = requests.get(

            url,

            headers={"User-Agent": USER_AGENT},

            timeout=REQUEST_TIMEOUT_SECONDS
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Strip non-content elements before extracting text.
        for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "svg"]):

            tag.decompose()

        title = ""

        if soup.title and soup.title.string:

            title = soup.title.string.strip()

        meta_description = ""

        meta_tag = soup.find("meta", attrs={"name": "description"})

        if meta_tag and meta_tag.get("content"):

            meta_description = meta_tag["content"].strip()

        main = soup.find("main") or soup.body

        if not main:

            return None

        text = main.get_text(separator=" ", strip=True)

        text = " ".join(text.split())

        if not text:

            return None

        return {

            "url": url,

            "title": title,

            "meta_description": meta_description,

            "text": text
        }

    except Exception as e:

        print(f"Error scraping {url}: {e}")

        return None


# =========================================================
# Main Entry Point
# =========================================================
def load_web_documents(max_pages=DEFAULT_MAX_PAGES):

    """
    Scrape Accion Labs' own site (via its sitemap) into
    Document objects, ready to be chunked and embedded
    alongside the rest of the knowledge base.
    """

    try:

        urls = fetch_sitemap_urls()

    except Exception as e:

        print(f"Could not fetch sitemap, skipping web scrape: {e}")

        return []

    allowed_urls = [u for u in urls if is_allowed(u)]

    skipped = len(urls) - len(allowed_urls)

    if skipped:

        print(f"Skipping {skipped} sitemap URL(s) disallowed by robots.txt")

    if max_pages is not None:

        allowed_urls = allowed_urls[:max_pages]

    print(f"Scraping {len(allowed_urls)} page(s) from {SITE_ROOT}...")

    documents = []

    for i, url in enumerate(allowed_urls, start=1):

        page = scrape_page(url)

        if page:

            content = page["text"]

            if page["meta_description"]:

                content = f"{page['meta_description']}\n\n{content}"

            documents.append(
                Document(

                    page_content=content,

                    metadata={

                        "source": url,

                        "title": page["title"] or url,

                        "type": "web",

                        "image": "",

                        "video": "",

                        "pdf": "",

                        "link": url
                    }
                )
            )

        if i % 25 == 0 or i == len(allowed_urls):

            print(f"  Scraped {i}/{len(allowed_urls)} pages...")

        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Web scrape complete: {len(documents)} page(s) usable")

    return documents


if __name__ == "__main__":

    docs = load_web_documents(max_pages=5)

    for d in docs:

        print("\n---")
        print(d.metadata["source"])
        print(d.metadata["title"])
        print(d.page_content[:200])
