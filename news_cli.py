import argparse
import requests
import sqlite3
import pandas as pd
import sys

# --- CONFIGURATION ---
API_KEY = "b2dd06437f77428eb6b4690ffffa96ba"
DB_NAME = "news_aggregator.db"

# --- DATABASE SETUP ---
def setup_db():
    """Creates the SQLite database and table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # The UNIQUE constraint on 'url' ensures we don't save duplicates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            author TEXT,
            published_at TEXT,
            url TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# --- FETCH DATA ---
def fetch_news(keyword, source, date):
    """Fetches news from NewsAPI based on CLI filters."""
    url = "https://newsapi.org/v2/everything"
    
    # Build the query parameters
    params = {
        'apiKey': API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt'
    }
    if keyword: params['q'] = keyword
    if source: params['sources'] = source
    if date: params['from'] = date

    if not keyword and not source:
        print("Error: You must provide either a --keyword or a --source to search.")
        sys.exit(1)

    print("Fetching news...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        print(f"Failed to fetch news: {response.json().get('message')}")
        sys.exit(1)

# --- STORE & DEDUPLICATE ---
def save_to_db(articles):
    """Saves articles to SQLite, ignoring duplicates."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    added_count = 0
    for article in articles:
        try:
            cursor.execute('''
                INSERT INTO articles (title, source, author, published_at, url)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                article.get('title'),
                article.get('source', {}).get('name'),
                article.get('author'),
                article.get('publishedAt'),
                article.get('url')
            ))
            added_count += 1
        except sqlite3.IntegrityError:
            # This triggers if the URL already exists (Deduplication)
            continue 
            
    conn.commit()
    conn.close()
    print(f"Successfully saved {added_count} new unique articles to the database.")

# --- EXPORT DATA ---
def export_data(format_type):
    """Exports the SQLite database to CSV or Excel."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()

    if df.empty:
        print("The database is empty. Fetch some news first!")
        return

    if format_type == 'csv':
        df.to_csv("exported_news.csv", index=False)
        print("Data exported to exported_news.csv")
    elif format_type == 'excel':
        df.to_excel("exported_news.xlsx", index=False)
        print("Data exported to exported_news.xlsx")

# --- MAIN CLI LOGIC ---
def main():
    setup_db() # Ensure database is ready

    parser = argparse.ArgumentParser(description="A News Aggregator CLI")
    parser.add_argument('-k', '--keyword', type=str, help="Search keyword (e.g., technology)")
    parser.add_argument('-s', '--source', type=str, help="News source (e.g., bbc-news)")
    parser.add_argument('-d', '--date', type=str, help="Date from (YYYY-MM-DD)")
    parser.add_argument('-e', '--export', type=str, choices=['csv', 'excel'], help="Export format")

    args = parser.parse_args()

    # If the user provides search arguments, fetch and save
    if args.keyword or args.source or args.date:
        articles = fetch_news(args.keyword, args.source, args.date)
        if articles:
            save_to_db(articles)
        else:
            print("No articles found for those filters.")

    # If the user wants to export
    if args.export:
        export_data(args.export)

if __name__ == "__main__":
    main()