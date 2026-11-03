"""
CodeAlpha Data Analytics Internship - Task 3: Data Visualization
Turns the scraped books dataset (Task 1) into charts and a one-page dashboard.

Usage:
    python visualize.py                       # uses books_dataset.csv
    python visualize.py --csv other.csv
Works with the basic CSV (title, price, rating, stock) and automatically adds
category charts when the CSV was scraped with --details.
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")  # no display needed (works in Colab / servers)
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PALETTE = {"main": "#2E5BBA", "accent": "#E4572E", "good": "#3BA776", "grey": "#8A8F98"}
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"axes.titleweight": "bold", "axes.titlesize": 13, "figure.dpi": 110})


def load(path):
    df = pd.read_csv(path)
    df["in_stock"] = df["in_stock"].astype(str).str.lower().eq("true")
    df = df.drop_duplicates(subset="url").dropna(subset=["price_gbp", "rating"])
    df["rating"] = df["rating"].astype(int)
    return df


def save(fig, outdir, name):
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, name), bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ---------- individual charts (each draws on a given axis so the dashboard can reuse them) ----------
def price_hist(df, ax):
    sns.histplot(df["price_gbp"], bins=20, color=PALETTE["main"], ax=ax)
    ax.axvline(df["price_gbp"].median(), color=PALETTE["accent"], ls="--",
               label=f"Median £{df['price_gbp'].median():.2f}")
    ax.set(title="How much do books cost?", xlabel="Price (£)", ylabel="Number of books")
    ax.legend()


def rating_counts(df, ax):
    counts = df["rating"].value_counts().sort_index()
    ax.bar(counts.index.astype(str), counts.values, color=PALETTE["main"])
    for x, v in zip(counts.index.astype(str), counts.values):
        ax.text(x, v, str(v), ha="center", va="bottom", fontsize=9)
    ax.set(title="Star rating distribution", xlabel="Stars", ylabel="Number of books")


def price_by_rating(df, ax):
    sns.boxplot(data=df, x="rating", y="price_gbp", color=PALETTE["main"], ax=ax)
    ax.set(title="Does a higher rating mean a higher price?", xlabel="Stars", ylabel="Price (£)")


def stock_chart(df, ax):
    s = df["in_stock"].map({True: "In stock", False: "Out of stock"}).value_counts()
    ax.pie(s.values, labels=s.index, autopct="%1.0f%%", startangle=90,
           colors=[PALETTE["good"], PALETTE["accent"]][: len(s)])
    ax.set_title("Stock availability")


def top_books(df, ax, n=8):
    top = df.nlargest(n, "price_gbp").iloc[::-1]
    labels = top["title"].str.slice(0, 32) + top["title"].apply(lambda t: "…" if len(t) > 32 else "")
    ax.barh(labels, top["price_gbp"], color=PALETTE["accent"])
    ax.set(title=f"Top {n} most expensive books", xlabel="Price (£)")


def category_price(df, ax, n=12):
    g = df.groupby("category")["price_gbp"].agg(["mean", "count"])
    g = g[g["count"] >= 5].nlargest(n, "mean").iloc[::-1]
    ax.barh(g.index, g["mean"], color=PALETTE["main"])
    ax.set(title=f"Average price by category (top {len(g)}, 5+ books)", xlabel="Average price (£)")


def category_count(df, ax, n=12):
    c = df["category"].value_counts().head(n).iloc[::-1]
    ax.barh(c.index, c.values, color=PALETTE["good"])
    ax.set(title=f"Most common categories (top {len(c)})", xlabel="Number of books")


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="books_dataset.csv")
    ap.add_argument("--out", default="charts")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df = load(args.csv)
    has_cat = "category" in df.columns and df["category"].notna().any()
    print(f"Loaded {len(df)} books (category data: {has_cat})")

    singles = [("01_price_distribution.png", price_hist, (8, 5)),
               ("02_rating_distribution.png", rating_counts, (7, 5)),
               ("03_price_by_rating.png", price_by_rating, (8, 5)),
               ("04_stock_availability.png", stock_chart, (6, 6)),
               ("05_most_expensive_books.png", top_books, (9, 5))]
    if has_cat:
        singles += [("06_avg_price_by_category.png", category_price, (9, 6)),
                    ("07_books_per_category.png", category_count, (9, 6))]
    for name, fn, size in singles:
        fig, ax = plt.subplots(figsize=size)
        fn(df, ax)
        save(fig, args.out, name)

    # dashboard
    panels = [price_hist, rating_counts, price_by_rating, stock_chart]
    panels += [category_price, category_count] if has_cat else [top_books]
    cols = 2
    rows = (len(panels) + 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(14, 5 * rows))
    for ax, fn in zip(axes.flat, panels):
        fn(df, ax)
    for ax in list(axes.flat)[len(panels):]:
        ax.axis("off")
    fig.suptitle(f"Books to Scrape - Dashboard ({len(df)} books)", fontsize=18, fontweight="bold", y=1.01)
    save(fig, args.out, "00_dashboard.png")

    # key findings printed for the video / README
    corr = df["price_gbp"].corr(df["rating"])
    print("\nKEY FINDINGS")
    print(f"- Average price £{df['price_gbp'].mean():.2f}, median £{df['price_gbp'].median():.2f}, "
          f"range £{df['price_gbp'].min():.2f}-£{df['price_gbp'].max():.2f}")
    print(f"- Most common rating: {df['rating'].mode()[0]} stars; average {df['rating'].mean():.2f}")
    print(f"- Price vs rating correlation: {corr:.2f} ({'weak' if abs(corr) < 0.3 else 'notable'})")
    print(f"- {df['in_stock'].mean():.0%} of books are in stock")
    if has_cat:
        g = df.groupby("category")["price_gbp"].agg(["mean", "count"])
        g = g[g["count"] >= 5]
        print(f"- Most expensive category (5+ books): {g['mean'].idxmax()} (£{g['mean'].max():.2f})")
        print(f"- Cheapest category (5+ books): {g['mean'].idxmin()} (£{g['mean'].min():.2f})")


if __name__ == "__main__":
    main()
