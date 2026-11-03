# CodeAlpha_DataVisualization

**CodeAlpha Data Analytics Internship, Task 3: Data Visualization**

Visualizes the book dataset scraped in Task 1 (`CodeAlpha_WebScraping`) using Matplotlib and Seaborn.

## Charts produced (`charts/` folder)
| File | Question it answers |
|---|---|
| 00_dashboard.png | One-page summary of everything |
| 01_price_distribution | How much do books cost? |
| 02_rating_distribution | How are ratings spread? |
| 03_price_by_rating | Do better-rated books cost more? |
| 04_stock_availability | How much is in stock? |
| 05_most_expensive_books | Which books cost the most? |
| 06_avg_price_by_category | Which genres are priciest? (needs `--details` data) |
| 07_books_per_category | Which genres are most common? (needs `--details` data) |

## Run it
```bash
pip install -r requirements.txt
python visualize.py                 # reads books_dataset.csv, writes charts/
```
Use the full 1,000-book CSV (scraped with `--details`) to get the category charts.

## Key findings
Printed by the script at the end of each run. Add the final numbers from your full dataset here.
