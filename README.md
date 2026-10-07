# Online Bookstore Price & Rating Analysis (Web Scraping Project)

**CodeAlpha Data Analytics Internship – Task 1: Web Scraping**

## Objective
Use Python to collect data from a public website, build a custom dataset, clean it, and extract basic insights.

## Problem Statement
An online bookstore lists 1000 books across many categories. Collecting this by hand is slow. This project automates the collection and answers: *Which categories have the most books? How are ratings distributed? Does a higher rating mean a higher price?*

## Website / Source
[Books to Scrape](https://books.toscrape.com) – a demo website created specifically for practising web scraping (fictional store, 1,000 books, 20 per page, 50 pages).

## Technologies Used
Python 3, Windows, VS Code / any editor, Git & GitHub.

## Python Libraries
| Library | Purpose |
|---|---|
| `requests` | Download web pages |
| `beautifulsoup4` | Parse HTML and find elements |
| `pandas` | Store, clean and analyse data |
| `matplotlib` | Create charts |

## Methodology
1. Send a request to the listing page and parse the HTML with BeautifulSoup.
2. Extract title, price, rating, availability and URL for each book.
3. Follow each book's link to collect its category and stock count.
4. Follow the "next" button to scrape all pages (pagination).
5. Use try/except, timeouts, retries and safe defaults to handle errors and missing values.
6. Save raw data to `scraped_data.csv`.
7. Clean the data and save `cleaned_data.csv`.
8. Analyse and visualise with pandas and matplotlib.

## HTML Elements / Selectors Used
| Data | Selector |
|---|---|
| Book container | `article.product_pod` |
| Title and link | `h3 a` (`title` and `href` attributes) |
| Price | `p.price_color` |
| Rating | `p.star-rating` (word in the CSS class, e.g. `Three`) |
| Availability | `p.availability` |
| Next page | `li.next a` |
| Category (book page) | `ul.breadcrumb li` (3rd item) |
| Stock count (book page) | `p.availability` text, e.g. "In stock (22 available)" |

## Data Fields Collected
`title`, `price`, `rating`, `availability`, `product_url`, `page_number`, `category`, `stock_count`

## Data Cleaning Process
- Removed duplicate books (based on `product_url`).
- Stripped extra spaces from text columns.
- Converted price from text (`£51.77`) to a float (`price_gbp`).
- Converted rating from words (`Three`) to numbers (`rating_num`).
- Filled missing categories with "Unknown" and missing stock counts with 0.
- Dropped rows missing a title or price.
- Set suitable data types (int, float, category).

## Analysis Performed
- Number of records and categories
- Average, median, minimum and maximum price
- Book count per rating and per category
- Average price by rating and by category

## Results
> Replace this section with YOUR actual results after running the code (copy numbers from the `analysis.py` output).

- Total records: `500`
- Average price: `£34.96`
- Cheapest book: `In Her Wake` (£12.84)
- Most expensive book: `Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981–1991` (£57.25)
- Most common category: `Default` (7 books)
- Most common rating: `5 stars` (10 books)
Charts are saved in the `charts/` folder:
`rating_distribution.png`, `top_categories.png`, `avg_price_by_rating.png`

## Conclusion
> Write 3–4 sentences in your own words based on your results, e.g. whether price appears related to rating, which categories dominate, and what you learned about HTML structure, pagination and data cleaning.

## Ethical / Legal Scraping Note
This project scrapes only a website intentionally built for scraping practice. The script uses a polite delay between requests, a timeout, and a descriptive User-Agent, and does not collect any personal data. Always check a website's `robots.txt` and Terms of Service before scraping, and never scrape sites that prohibit it.

## How to Run
```
pip install -r requirements.txt
python web_scraping.py     # set TEST_MODE = False inside the file for the full 1000 books
python analysis.py
```
