#!/usr/bin/env python3
"""
Web Scraper — Crawls a website, follows internal links, extracts page data,
and exports results to CSV or JSON.

Requirements:
    pip install requests beautifulsoup4 lxml

Usage:
    python scraper.py --url https://example.com --output csv --max-pages 50
    python scraper.py --url https://example.com --output json --max-depth 3
"""

import argparse
import csv
import json
import logging
import time
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Headers ─────────────────────────────────────────────────────────────────
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def is_same_domain(url: str, base_domain: str) -> bool:
    """Return True if the URL belongs to the same domain as base_domain."""
    parsed = urlparse(url)
    return parsed.netloc == base_domain or parsed.netloc == ""


def normalize_url(url: str, base: str) -> str | None:
    """Resolve relative URLs and strip fragments. Return None for non-HTTP URLs."""
    full = urljoin(base, url).split("#")[0].rstrip("/")
    scheme = urlparse(full).scheme
    if scheme not in ("http", "https"):
        return None
    return full


def extract_page_data(url: str, soup: BeautifulSoup) -> dict:
    """Extract structured data from a parsed HTML page."""
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    # Meta description
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else ""

    # All headings
    headings = {
        f"h{level}": [tag.get_text(strip=True) for tag in soup.find_all(f"h{level}")]
        for level in range(1, 7)
    }

    # Body text (first 500 chars as a preview)
    body = soup.find("body")
    body_text = body.get_text(separator=" ", strip=True) if body else ""
    body_preview = " ".join(body_text.split())[:500]

    # All links on the page
    links = [
        normalize_url(a["href"], url)
        for a in soup.find_all("a", href=True)
        if normalize_url(a["href"], url)
    ]

    # Images (src + alt)
    images = [
        {"src": normalize_url(img.get("src", ""), url), "alt": img.get("alt", "")}
        for img in soup.find_all("img")
        if img.get("src")
    ]

    return {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "h1": headings["h1"],
        "h2": headings["h2"],
        "h3": headings["h3"],
        "body_preview": body_preview,
        "images_count": len(images),
        "images": images,
        "links_count": len(links),
        "internal_links": [],   # filled in during crawl
        "external_links": [],   # filled in during crawl
    }


# ─── Crawler ─────────────────────────────────────────────────────────────────

def crawl(
    start_url: str,
    max_pages: int = 100,
    max_depth: int = 5,
    delay: float = 0.5,
    timeout: int = 10,
) -> list[dict]:
    """
    BFS crawl starting from `start_url`.

    Args:
        start_url:  The seed URL.
        max_pages:  Maximum number of pages to visit.
        max_depth:  Maximum link depth from the start URL.
        delay:      Seconds to wait between requests (be polite!).
        timeout:    HTTP request timeout in seconds.

    Returns:
        List of page data dicts.
    """
    base_domain = urlparse(start_url).netloc
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    visited: set[str] = set()
    results: list[dict] = []

    # Queue items: (url, depth)
    queue: deque[tuple[str, int]] = deque([(start_url, 0)])

    while queue and len(results) < max_pages:
        url, depth = queue.popleft()

        if url in visited:
            continue
        if depth > max_depth:
            log.debug("Skipping %s — max depth reached", url)
            continue

        visited.add(url)
        log.info("[%d/%d] Scraping (depth %d): %s", len(results) + 1, max_pages, depth, url)

        try:
            response = session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                log.debug("Skipping non-HTML content: %s", url)
                continue
        except requests.RequestException as exc:
            log.warning("Failed to fetch %s: %s", url, exc)
            continue

        soup = BeautifulSoup(response.text, "lxml")
        page_data = extract_page_data(url, soup)

        # Categorise links into internal / external and enqueue internal ones
        internal: list[str] = []
        external: list[str] = []
        for link in set(page_data.pop("internal_links", []) + page_data["links_count"] * []):
            pass  # handled below

        all_links = [
            normalize_url(a["href"], url)
            for a in soup.find_all("a", href=True)
        ]
        all_links = [lnk for lnk in all_links if lnk]

        for link in all_links:
            if is_same_domain(link, base_domain):
                internal.append(link)
                if link not in visited and depth + 1 <= max_depth:
                    queue.append((link, depth + 1))
            else:
                external.append(link)

        page_data["internal_links"] = list(dict.fromkeys(internal))   # deduplicated
        page_data["external_links"] = list(dict.fromkeys(external))
        page_data["links_count"] = len(all_links)
        page_data["depth"] = depth

        results.append(page_data)
        time.sleep(delay)

    log.info("Crawl complete. %d pages scraped.", len(results))
    return results


# ─── Export ──────────────────────────────────────────────────────────────────

def export_json(data: list[dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info("JSON saved → %s", filepath)


def export_csv(data: list[dict], filepath: str) -> None:
    """Flatten nested fields for CSV export."""
    flat_rows = []
    for page in data:
        row = {
            "url":              page.get("url", ""),
            "depth":            page.get("depth", ""),
            "title":            page.get("title", ""),
            "meta_description": page.get("meta_description", ""),
            "h1":               " | ".join(page.get("h1", [])),
            "h2":               " | ".join(page.get("h2", [])),
            "h3":               " | ".join(page.get("h3", [])),
            "body_preview":     page.get("body_preview", ""),
            "images_count":     page.get("images_count", 0),
            "links_count":      page.get("links_count", 0),
            "internal_links":   " | ".join(page.get("internal_links", [])),
            "external_links":   " | ".join(page.get("external_links", [])),
        }
        flat_rows.append(row)

    if not flat_rows:
        log.warning("No data to write.")
        return

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat_rows[0].keys()))
        writer.writeheader()
        writer.writerows(flat_rows)

    log.info("CSV saved → %s", filepath)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Crawl a website and export scraped data to CSV or JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--url",        required=True,  help="Seed URL to start crawling from")
    parser.add_argument("--output",     default="csv",  choices=["csv", "json", "both"],
                        help="Output format")
    parser.add_argument("--max-pages",  type=int, default=50,
                        help="Maximum number of pages to scrape")
    parser.add_argument("--max-depth",  type=int, default=3,
                        help="Maximum link depth from the seed URL")
    parser.add_argument("--delay",      type=float, default=0.5,
                        help="Delay (seconds) between requests")
    parser.add_argument("--timeout",    type=int, default=10,
                        help="HTTP request timeout (seconds)")
    parser.add_argument("--out-file",   default="scraped_data",
                        help="Output filename (without extension)")
    return parser.parse_args()


def main():
    args = parse_args()

    log.info("Starting crawl: %s", args.url)
    log.info("Settings — max_pages=%d, max_depth=%d, delay=%.1fs",
             args.max_pages, args.max_depth, args.delay)

    data = crawl(
        start_url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay=args.delay,
        timeout=args.timeout,
    )

    if not data:
        log.error("No data scraped. Check the URL and your network connection.")
        return

    if args.output in ("csv", "both"):
        export_csv(data, f"{args.out_file}.csv")
    if args.output in ("json", "both"):
        export_json(data, f"{args.out_file}.json")


if __name__ == "__main__":
    main()