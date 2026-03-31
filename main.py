#!/usr/bin/env python3
"""
main.py — Personal Expense Categorizer CLI
==========================================
Course: Fundamentals of AI and ML
Project: Bring Your Own Project (BYOP)

Architecture:
  1. Prolog Rules Engine  → keyword + amount-based Horn clause matching
  2. K-Means ML Fallback  → clusters uncategorized transactions
  3. Matplotlib Charts    → pie chart, bar chart, trend analysis

Usage:
  python main.py                        # interactive menu
  python main.py --load data/expenses.csv
  python main.py --add                  # add single transaction
"""

import os
import sys
import csv
import argparse
from datetime import datetime
from collections import defaultdict

from prolog_rules import PrologEngine
from ml_categorizer import MLCategorizer
from charts import pie_chart, bar_chart, monthly_trend_chart, stacked_bar_chart
import sample_data as sd

# ── Terminal colours ────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"

def c(text, colour): return f"{colour}{text}{C.RESET}"
def bold(text):      return c(text, C.BOLD)
def ok(text):        return c(f"✅  {text}", C.GREEN)
def warn(text):      return c(f"⚠️  {text}", C.YELLOW)
def info(text):      return c(f"ℹ️  {text}", C.CYAN)
def err(text):       return c(f"❌  {text}", C.RED)


# ── Data store ──────────────────────────────────────────────────────────────
transactions: list[dict] = []   # list of {date, description, amount, category, method}
CHARTS_DIR = "charts"
DATA_FILE  = "data/expenses.csv"

prolog = PrologEngine()
ml     = MLCategorizer(n_clusters=8)


# ── Helpers ─────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input(f"\n{C.YELLOW}Press Enter to continue...{C.RESET}")

def _fit_ml():
    """Fit the ML model on currently loaded transactions (excluding 'Other')."""
    descs = [t["description"] for t in transactions]
    cats  = [t["category"]    for t in transactions]
    if len(descs) >= ml.n_clusters:
        ml.fit(descs, cats)

def categorize(description: str, amount: float) -> tuple[str, str]:
    """
    Returns (category, method) where method is 'prolog' or 'ml'.
    """
    cat = prolog.query(description, amount)
    if cat != "Other":
        return cat, "prolog"
    # ML fallback
    ml_cat = ml.predict(description)
    return ml_cat, "ml"

def load_csv(filepath: str) -> int:
    """Load transactions from a CSV file. Returns count loaded."""
    global transactions
    if not os.path.exists(filepath):
        print(err(f"File not found: {filepath}"))
        return 0
    loaded = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                desc   = row.get("description", "").strip()
                amount = float(row.get("amount", 0))
                date_s = row.get("date", "")
                # Re-categorize even if category column exists
                cat, method = categorize(desc, amount)
                loaded.append({
                    "date":        date_s,
                    "description": desc,
                    "amount":      amount,
                    "category":    cat,
                    "method":      method,
                })
            except (ValueError, KeyError):
                continue
    transactions = loaded
    _fit_ml()
    return len(loaded)

def save_csv(filepath: str):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","description","amount","category","method"])
        writer.writeheader()
        writer.writerows(transactions)

def category_totals() -> dict:
    totals = defaultdict(float)
    for t in transactions:
        totals[t["category"]] += t["amount"]
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))

def monthly_totals() -> dict:
    monthly = defaultdict(float)
    for t in transactions:
        try:
            d = datetime.strptime(t["date"], "%Y-%m-%d")
            key = d.strftime("%b %Y")
            monthly[key] += t["amount"]
        except ValueError:
            pass
    # Sort chronologically
    def month_key(s):
        try: return datetime.strptime(s, "%b %Y")
        except: return datetime.min
    return dict(sorted(monthly.items(), key=lambda x: month_key(x[0])))

def monthly_category_totals() -> dict:
    data = defaultdict(lambda: defaultdict(float))
    for t in transactions:
        try:
            d = datetime.strptime(t["date"], "%Y-%m-%d")
            key = d.strftime("%b %Y")
            data[key][t["category"]] += t["amount"]
        except ValueError:
            pass
    def month_key(s):
        try: return datetime.strptime(s, "%b %Y")
        except: return datetime.min
    return dict(sorted(data.items(), key=lambda x: month_key(x[0])))


# ── Menu actions ─────────────────────────────────────────────────────────────

def action_load():
    print(f"\n{bold('Load Transactions')}")
    path = input(f"  CSV path [{DATA_FILE}]: ").strip() or DATA_FILE
    n = load_csv(path)
    if n:
        print(ok(f"Loaded {n} transactions from {path}"))
    pause()

def action_generate_sample():
    sd.generate_csv(DATA_FILE)
    n = load_csv(DATA_FILE)
    print(ok(f"Sample data generated and loaded ({n} transactions)"))
    pause()

def action_add_transaction():
    print(f"\n{bold('Add Transaction')}")
    date_s = input("  Date (YYYY-MM-DD) [today]: ").strip() or datetime.today().strftime("%Y-%m-%d")
    desc   = input("  Description: ").strip()
    try:
        amount = float(input("  Amount (₹): ").strip())
    except ValueError:
        print(err("Invalid amount")); pause(); return

    cat, method = categorize(desc, amount)
    print(f"\n  {bold('Auto-categorized:')} {c(cat, C.GREEN)}  (via {method})")

    override = input("  Override category? (Enter to keep / type new): ").strip()
    if override:
        cat = override
        method = "manual"

    transactions.append({"date": date_s, "description": desc,
                          "amount": amount, "category": cat, "method": method})
    _fit_ml()
    save_csv(DATA_FILE)
    print(ok(f"Transaction added: {desc} → {cat}"))
    pause()

def action_view_transactions():
    if not transactions:
        print(warn("No transactions loaded. Use option 3 to load or generate data.")); pause(); return

    print(f"\n{bold('All Transactions')}  ({len(transactions)} total)\n")
    header = f"{'Date':<12} {'Description':<38} {'Amount':>10}  {'Category':<22} {'Via'}"
    print(c(header, C.BLUE))
    print("─" * 95)
    for t in transactions:
        method_badge = c("●", C.GREEN) if t["method"] == "prolog" else c("◆", C.MAGENTA)
        desc_short = t["description"][:36] + ("…" if len(t["description"]) > 36 else "")
        print(f"{t['date']:<12} {desc_short:<38} ₹{t['amount']:>9,.2f}  {t['category']:<22} {method_badge}")
    print(f"\n  {c('●', C.GREEN)} = Prolog rule   {c('◆', C.MAGENTA)} = ML cluster")
    pause()

def action_summary():
    if not transactions:
        print(warn("No transactions loaded.")); pause(); return

    totals = category_totals()
    grand_total = sum(totals.values())

    print(f"\n{bold('Spending Summary')}\n")
    print(f"  {'Category':<25} {'Total':>12}   {'Share':>7}")
    print("  " + "─" * 48)
    for cat, amt in totals.items():
        pct = amt / grand_total * 100
        bar = "█" * int(pct / 3)
        print(f"  {cat:<25} ₹{amt:>11,.2f}   {pct:>5.1f}%  {c(bar, C.CYAN)}")
    print("  " + "─" * 48)
    print(f"  {'TOTAL':<25} ₹{grand_total:>11,.2f}")

    prolog_count = sum(1 for t in transactions if t["method"] == "prolog")
    ml_count     = sum(1 for t in transactions if t["method"] == "ml")
    manual_count = sum(1 for t in transactions if t["method"] == "manual")
    print(f"\n  Categorized by: {c(f'Prolog {prolog_count}', C.GREEN)}  |  "
          f"{c(f'ML {ml_count}', C.MAGENTA)}  |  {c(f'Manual {manual_count}', C.YELLOW)}")
    pause()

def action_charts():
    if not transactions:
        print(warn("No transactions loaded.")); pause(); return

    os.makedirs(CHARTS_DIR, exist_ok=True)
    totals = category_totals()
    monthly = monthly_totals()
    monthly_cat = monthly_category_totals()

    print(f"\n{bold('Generating Charts...')}")

    p1 = pie_chart(totals, f"{CHARTS_DIR}/pie_chart.png", "Spending by Category")
    print(ok(f"Pie chart saved → {p1}"))

    p2 = bar_chart(totals, f"{CHARTS_DIR}/bar_chart.png", "Expenses by Category")
    print(ok(f"Bar chart saved → {p2}"))

    if len(monthly) > 1:
        p3 = monthly_trend_chart(monthly, f"{CHARTS_DIR}/monthly_trend.png")
        print(ok(f"Monthly trend chart saved → {p3}"))

        p4 = stacked_bar_chart(monthly_cat, f"{CHARTS_DIR}/stacked_bar.png")
        print(ok(f"Stacked bar chart saved → {p4}"))
    else:
        print(info("Need 2+ months of data for trend charts."))

    print(f"\n  Charts saved in: {c(CHARTS_DIR+'/', C.CYAN)}")
    pause()

def action_prolog_explain():
    print(f"\n{bold('Prolog Rule Explainer')}")
    desc   = input("  Enter transaction description: ").strip()
    try:
        amount = float(input("  Enter amount (₹): ").strip())
    except ValueError:
        print(err("Invalid amount")); pause(); return

    explanation = prolog.explain(desc, amount)
    cat, method = categorize(desc, amount)

    print(f"\n  {bold('Result:')} {c(cat, C.GREEN)}  (method: {method})")
    print(f"\n  {bold('Prolog Trace:')}")
    for line in explanation.split("\n"):
        print(f"    {c(line, C.CYAN)}")
    pause()

def action_view_rules():
    print(prolog.list_rules())
    pause()

def action_export():
    if not transactions:
        print(warn("No transactions to export.")); pause(); return
    path = input(f"  Export path [data/categorized.csv]: ").strip() or "data/categorized.csv"
    save_csv(path)
    print(ok(f"Exported {len(transactions)} transactions to {path}"))
    pause()


# ── Main menu ────────────────────────────────────────────────────────────────

MENU = [
    ("Generate sample data (Mumbai expenses)", action_generate_sample),
    ("Load CSV file",                          action_load),
    ("Add a transaction manually",             action_add_transaction),
    ("View all transactions",                  action_view_transactions),
    ("View spending summary",                  action_summary),
    ("Generate charts (pie + bar + trend)",    action_charts),
    ("Explain Prolog categorization",          action_prolog_explain),
    ("View Prolog knowledge base (rules)",     action_view_rules),
    ("Export categorized data to CSV",         action_export),
    ("Exit",                                   None),
]

def main():
    parser = argparse.ArgumentParser(description="Personal Expense Categorizer")
    parser.add_argument("--load", metavar="FILE", help="Load a CSV file on startup")
    parser.add_argument("--add",  action="store_true", help="Add a transaction interactively")
    args = parser.parse_args()

    # Auto-load if default data file exists
    if args.load:
        n = load_csv(args.load)
        print(ok(f"Loaded {n} transactions from {args.load}"))
    elif os.path.exists(DATA_FILE):
        n = load_csv(DATA_FILE)
        if n:
            print(info(f"Auto-loaded {n} transactions from {DATA_FILE}"))

    if args.add:
        action_add_transaction()
        return

    while True:
        clear()
        print(BANNER)
        if transactions:
            totals = category_totals()
            grand  = sum(totals.values())
            print(f"  {info(f'Loaded: {len(transactions)} transactions  |  Total: ₹{grand:,.2f}')}\n")

        for i, (label, _) in enumerate(MENU, 1):
            colour = C.RED if i == len(MENU) else C.CYAN
            print(f"  {c(str(i), colour)}. {label}")

        print()
        choice = input(f"  {bold('Choose an option:')} ").strip()

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(MENU):
                raise ValueError
        except ValueError:
            continue

        label, action = MENU[idx]
        if action is None:
            print(f"\n{c('Goodbye! 👋', C.GREEN)}\n")
            break
        clear()
        print(f"\n{c('─'*55, C.BLUE)}")
        print(f"  {bold(label)}")
        print(f"{c('─'*55, C.BLUE)}\n")
        action()


if __name__ == "__main__":
    main()
