"""
web_scraping.py
---------------
Scrapes book data from https://books.toscrape.com (a practice website made
for learning web scraping) and saves it to scraped_data.csv.

Run:  python web_scraping.py
"""

import re
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# SETTINGS (change these if you want)
# ----------------------------------------------------------------------
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
OUTPUT_FILE = "scraped_data.csv"

# TEST_MODE = True  -> scrapes only 2 pages (40 books) so you can test quickly.
# TEST_MODE = False -> scrapes ALL 50 pages (1000 books). Takes ~10-15 minutes.
TEST_MODE = True
TEST_PAGES = 25

DELAY_SECONDS = 0.1   # polite pause between requests (don't hammer the server)
TIMEOUT = 10          # give up on a request after 10 seconds
RETRIES = 3           # try each page up to 3 times

# A User-Agent tells the website who is visiting. Being honest is good practice.
HEADERS = {"User-Agent": "Mozilla/5.0 (Internship learning project; contact: student)"}

# The site stores ratings as words in the CSS class, e.g. "star-rating Three"
# We keep the word here and convert it to a number later, during cleaning.


# ----------------------------------------------------------------------
# STEP 1: A function that downloads a page safely
# ----------------------------------------------------------------------
def get_html(url):
    """Download a URL and return a BeautifulSoup object (or None if it fails)."""
    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()          # raises an error for 404, 500, etc.
            response.encoding = "utf-8"          # fixes the "Â£" symbol problem
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as error:
            print(f"   Attempt {attempt}/{RETRIES} failed for {url}: {error}")
            time.sleep(2)                        # wait before retrying
    return None                                  # all attempts failed


# ----------------------------------------------------------------------
# STEP 2: Extract fields from ONE book box on a listing page
# ----------------------------------------------------------------------
def parse_book(book, page_url, page_number):
    """Take one <article class="product_pod"> and return a dictionary of fields."""
    # Each field is wrapped so that a missing tag gives None instead of crashing.

    # Title: full title is in the 'title' attribute of the link inside <h3>
    link_tag = book.select_one("h3 a")
    title = link_tag.get("title") if link_tag else None

    # Product URL: the href is relative, so urljoin builds the full address
    product_url = urljoin(page_url, link_tag["href"]) if link_tag else None

    # Price text, e.g. "£51.77"
    price_tag = book.select_one("p.price_color")
    price = price_tag.get_text(strip=True) if price_tag else None

    # Rating: the class list looks like ['star-rating', 'Three']
    rating_tag = book.select_one("p.star-rating")
    rating = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        rating = next((c for c in classes if c != "star-rating"), None)

    # Availability text, e.g. "In stock"
    avail_tag = book.select_one("p.availability")
    availability = avail_tag.get_text(strip=True) if avail_tag else None

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "product_url": product_url,
        "page_number": page_number,
    }


# ----------------------------------------------------------------------
# STEP 3: Visit a book's own page to get category and stock count
# ----------------------------------------------------------------------
def get_book_details(product_url):
    """Open one book page and return (category, stock_count)."""
    if not product_url:
        return None, None

    soup = get_html(product_url)
    if soup is None:
        return None, None

    # Category: the breadcrumb is Home > Books > <Category> > <Title>
    category = None
    crumbs = soup.select("ul.breadcrumb li")
    if len(crumbs) >= 3:
        category = crumbs[2].get_text(strip=True)

    # Stock count: text looks like "In stock (22 available)"
    stock_count = None
    avail_tag = soup.select_one("p.availability")
    if avail_tag:
        match = re.search(r"\((\d+) available\)", avail_tag.get_text())
        if match:
            stock_count = int(match.group(1))

    return category, stock_count


# ----------------------------------------------------------------------
# STEP 4: Main program - loop through pages (pagination)
# ----------------------------------------------------------------------
def main():
    all_books = []
    url = START_URL
    page_number = 1

    while url:
        print(f"Scraping page {page_number}: {url}")
        soup = get_html(url)

        if soup is None:
            print("Could not load this page. Stopping.")
            break

        books_on_page = soup.select("article.product_pod")
        if not books_on_page:
            print("No books found - the HTML structure may have changed. Stopping.")
            break

        for book in books_on_page:
            record = parse_book(book, url, page_number)

            # Navigate into the book's own page for extra details
            category, stock_count = get_book_details(record["product_url"])
            record["category"] = category
            record["stock_count"] = stock_count

            all_books.append(record)
            time.sleep(DELAY_SECONDS)

        print(f"   Collected {len(books_on_page)} books (total so far: {len(all_books)})")

        # Stop early in test mode
        if TEST_MODE and page_number >= TEST_PAGES:
            print("TEST_MODE is ON - stopping early.")
            break

        # Pagination: find the "next" button. If there isn't one, we are done.
        next_link = soup.select_one("li.next a")
        url = urljoin(url, next_link["href"]) if next_link else None
        page_number += 1

    # Save everything to CSV using pandas
    if all_books:
        df = pd.DataFrame(all_books)
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"\nDone! Saved {len(df)} records to {OUTPUT_FILE}")
        print(df.head())
    else:
        print("\nNo data collected. Check your internet connection or selectors.")


if __name__ == "__main__":
    main()
