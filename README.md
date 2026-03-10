# News Aggregator CLI 📰

A powerful Command-Line Interface (CLI) application built in Python that fetches, filters, stores, and exports live news articles. Developed as the 4th capstone project during my Python Programming Internship at Syntecxhub, this tool combines API integration, database management, and automated data exporting into one cohesive application.

## 🚀 Features
* **Live News Fetching:** Integrates with NewsAPI to pull real-time articles and headlines.
* **Smart CLI Filters:** Allows users to search for news by specific keywords, sources, or publication dates directly from the terminal.
* **Local Database Storage:** Uses SQLite to store fetched articles for offline querying.
* **Automatic Deduplication:** Prevents the same article from being saved twice using database URL constraints.
* **Automated Data Export:** Leverages `pandas` to easily export the saved news database into readable `.csv` or `.xlsx` (Excel) formats.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Libraries:** `requests`, `argparse`, `sqlite3`, `pandas`, `openpyxl`
* **API:** NewsAPI
