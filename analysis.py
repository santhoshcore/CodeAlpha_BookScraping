"""
analysis.py
-----------
Inspects, cleans and analyses scraped_data.csv, then saves cleaned_data.csv
and 3 charts in the 'charts' folder.

Run (after web_scraping.py):  python analysis.py
"""

import os

import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------------------------------------------------
# STEP 1: Load and inspect the raw data
# ----------------------------------------------------------------------
df = pd.read_csv("scraped_data.csv", encoding="utf-8-sig")

print("=" * 60)
print("RAW DATA INSPECTION")
print("=" * 60)
print("Shape (rows, columns):", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nColumn info:")
df.info()
print("\nMissing values per column:")
print(df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# ----------------------------------------------------------------------
# STEP 2: Clean the data
# ----------------------------------------------------------------------
# 2a. Remove duplicate books (same product URL = same book)
before = len(df)
df = df.drop_duplicates(subset="product_url")
print(f"\nRemoved {before - len(df)} duplicate rows")

# 2b. Remove extra spaces from text columns
for col in ["title", "category", "availability"]:
    df[col] = df[col].astype("string").str.strip()

# 2c. Price: "£51.77" -> 51.77 (float)
df["price_gbp"] = pd.to_numeric(
    df["price"].astype("string").str.replace(r"[^0-9.]", "", regex=True),
    errors="coerce",
)

# 2d. Rating: "Three" -> 3 (integer)
rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
df["rating_num"] = df["rating"].map(rating_map)

# 2e. Stock count -> number
df["stock_count"] = pd.to_numeric(df["stock_count"], errors="coerce")

# 2f. Missing values
df["category"] = df["category"].fillna("Unknown")          # missing text -> "Unknown"
df["stock_count"] = df["stock_count"].fillna(0)            # missing stock -> 0
df = df.dropna(subset=["title", "price_gbp"])              # a book without title/price is useless

# 2g. Convert to suitable data types
df["rating_num"] = df["rating_num"].astype("Int64")
df["stock_count"] = df["stock_count"].astype(int)
df["category"] = df["category"].astype("category")

# 2h. Keep only the useful columns, in a tidy order
df = df[["title", "category", "price_gbp", "rating_num",
         "availability", "stock_count", "product_url", "page_number"]]

df.to_csv("cleaned_data.csv", index=False, encoding="utf-8-sig")
print("Saved cleaned_data.csv")
print("\nCleaned data types:")
print(df.dtypes)

# ----------------------------------------------------------------------
# STEP 3: Analysis
# ----------------------------------------------------------------------
print("\n" + "=" * 60)
print("ANALYSIS RESULTS")
print("=" * 60)

print("Number of records:", len(df))
print("Number of categories:", df["category"].nunique())
print(f"Average price: £{df['price_gbp'].mean():.2f}")
print(f"Median price : £{df['price_gbp'].median():.2f}")

cheapest = df.loc[df["price_gbp"].idxmin()]
priciest = df.loc[df["price_gbp"].idxmax()]
print(f"Minimum price: £{cheapest['price_gbp']:.2f}  ({cheapest['title']})")
print(f"Maximum price: £{priciest['price_gbp']:.2f}  ({priciest['title']})")

print("\nBooks per rating:")
rating_counts = df["rating_num"].value_counts().sort_index()
print(rating_counts)

print("\nTop 10 categories by number of books:")
top_categories = df["category"].value_counts().head(10)
print(top_categories)

print("\nAverage price by rating:")
avg_price_by_rating = df.groupby("rating_num")["price_gbp"].mean().round(2)
print(avg_price_by_rating)

print("\nTop 5 categories by average price (categories with 5+ books):")
cat_stats = df.groupby("category", observed=True)["price_gbp"].agg(["count", "mean"])
print(cat_stats[cat_stats["count"] >= 5].sort_values("mean", ascending=False).head(5).round(2))

# ----------------------------------------------------------------------
# STEP 4: Charts (saved as PNG files in the 'charts' folder)
# ----------------------------------------------------------------------
os.makedirs("charts", exist_ok=True)

# Chart 1: number of books per rating
plt.figure(figsize=(7, 5))
rating_counts.plot(kind="bar", color="steelblue")
plt.title("Number of Books by Star Rating")
plt.xlabel("Star Rating")
plt.ylabel("Number of Books")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("charts/rating_distribution.png", dpi=150)
plt.show()

# Chart 2: top 10 categories
plt.figure(figsize=(9, 6))
top_categories.sort_values().plot(kind="barh", color="seagreen")
plt.title("Top 10 Categories by Number of Books")
plt.xlabel("Number of Books")
plt.ylabel("Category")
plt.tight_layout()
plt.savefig("charts/top_categories.png", dpi=150)
plt.show()

# Chart 3: average price by rating
plt.figure(figsize=(7, 5))
avg_price_by_rating.plot(kind="bar", color="darkorange")
plt.title("Average Price by Star Rating")
plt.xlabel("Star Rating")
plt.ylabel("Average Price (£)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("charts/avg_price_by_rating.png", dpi=150)
plt.show()

print("\nCharts saved in the 'charts' folder.")
