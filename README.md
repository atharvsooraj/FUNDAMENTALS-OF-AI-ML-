# 💰 Personal Expense Categorizer

A CLI-based personal finance tool that automatically categorizes your expenses using:
- **Prolog-style Rules Engine** — keyword + amount-based Horn clause matching
- **K-Means ML Clustering** — unsupervised fallback for uncategorized transactions
- **Matplotlib Visualizations** — pie charts, bar charts, and monthly trend analysis

> Built as a BYOP (Bring Your Own Project) submission for *Fundamentals of AI and ML*.

---

## 📁 Project Structure

```
expense_categorizer/
├── main.py            # CLI entry point — interactive menu
├── prolog_rules.py    # Pure-Python Prolog rules engine (knowledge base + inference)
├── ml_categorizer.py  # K-Means + TF-IDF ML categorization
├── charts.py          # Matplotlib chart generators
├── sample_data.py     # Synthetic Mumbai expense data generator
├── data/
│   └── expenses.csv   # Your transaction data (auto-created)
├── charts/            # Generated chart images (auto-created)
└── README.md
```

---

## 🚀 Setup

### Prerequisites
- Python 3.9+
- pip

### Install dependencies
```bash
pip install scikit-learn matplotlib numpy pandas
```

### Run the app
```bash
cd expense_categorizer
python main.py
```

---

## 🖥️ Usage

### Interactive Menu
```
python main.py
```
You'll see a numbered menu with these options:
1. **Generate sample data** — creates realistic Mumbai expense data
2. **Load CSV file** — load your own transactions
3. **Add a transaction** — manually enter a single expense
4. **View all transactions** — table view with colour-coded categorization method
5. **View spending summary** — totals per category with ASCII bar chart
6. **Generate charts** — saves pie/bar/trend charts to `charts/`
7. **Explain Prolog categorization** — shows which rule fired for any description
8. **View Prolog knowledge base** — lists all Horn clause rules
9. **Export categorized CSV** — save results

### Command-line flags
```bash
python main.py --load my_transactions.csv   # load file on startup
python main.py --add                         # quick-add a transaction
```

---

## 📄 CSV Format

Your input CSV should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `date` | YYYY-MM-DD | `2025-03-15` |
| `description` | Transaction description | `Zomato biryani order` |
| `amount` | Amount in ₹ | `320` |

The `category` column is optional — the app will re-categorize everything.

---

## 🧠 How It Works

### 1. Prolog Rules Engine (`prolog_rules.py`)
Implements a simplified Prolog inference engine in pure Python.

**Horn clause logic:**
```prolog
category(T, 'Food & Dining') :-
    keyword_match(T, [zomato, swiggy, restaurant, ...]).

category(T, 'Rent & Housing') :-
    amount(T, A), A > 5000.

category(_, 'Other').   % default fact
```

Rules fire top-to-bottom; the first match wins (Prolog cut semantics).

### 2. K-Means ML Fallback (`ml_categorizer.py`)
When no Prolog rule matches ("Other"), the transaction is classified using:
- **TF-IDF Vectorizer** — character n-gram features (handles short descriptions)
- **K-Means Clustering** — groups similar transactions
- **Majority vote** — assigns the most common Prolog-labelled category to each cluster

### 3. Matplotlib Charts (`charts.py`)
Four chart types are generated and saved as PNG files:
- `pie_chart.png` — spending share by category
- `bar_chart.png` — horizontal bar chart sorted by amount
- `monthly_trend.png` — total spending per month
- `stacked_bar.png` — category breakdown per month

---

## 📊 Sample Output

```
  Category                  Total          Share
  ────────────────────────────────────────────────
  Food & Dining             ₹  8,420.00   21.3%  ███████
  Rent & Housing            ₹ 12,000.00   30.4%  ██████████
  Groceries                 ₹  4,200.00   10.6%  ███
  Transport                 ₹  3,100.00    7.8%  ██
  ...
  ────────────────────────────────────────────────
  TOTAL                     ₹ 39,450.00

  Categorized by: Prolog 72  |  ML 6  |  Manual 2
```

---

## 🧪 Concepts Demonstrated

| Concept | Where Used |
|---------|------------|
| Knowledge Representation | `prolog_rules.py` — Horn clauses, facts, inference |
| Rule-based AI | Prolog engine with first-match semantics |
| Feature Engineering | TF-IDF character n-grams in `ml_categorizer.py` |
| Unsupervised Learning | K-Means clustering |
| Data Visualization | 4 chart types in `charts.py` |
| CLI Application Design | Argparse + interactive menu in `main.py` |

---

## 📝 Notes

- The Prolog engine is a pure-Python implementation — no SWI-Prolog installation required.
- Sample data reflects common Mumbai expenses (Zomato, BEST bus, MSEDCL, etc.).
- All amounts are in Indian Rupees (₹).

---

## 👤 Author

Submitted as BYOP Project — *Fundamentals of AI and ML*  
VIT — 2025–26
