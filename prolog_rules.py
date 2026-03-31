"""
prolog_rules.py
---------------
A lightweight, pure-Python Prolog-style rules engine.
Rules are written as Python data structures that mirror Prolog Horn clauses.

Prolog logic used here:
  category(Transaction, Category) :- keyword_match(Transaction, Keywords), member(K, Keywords), contains(Description, K).

No external SWI-Prolog installation required.
"""

import re

# ---------------------------------------------------------------------------
# KNOWLEDGE BASE  (Prolog facts + rules encoded as Python dicts)
# ---------------------------------------------------------------------------

# Each rule is: { "category": str, "keywords": [str], "min_amount": float|None, "max_amount": float|None }
# Rules are evaluated top-to-bottom (first match wins) — classic Prolog cut behaviour.

RULES = [
    # ── Food & Dining ───────────────────────────────────────────────────────
    {
        "category": "Food & Dining",
        "keywords": [
            "zomato", "swiggy", "restaurant", "café", "cafe", "coffee",
            "pizza", "burger", "biryani", "hotel", "dhaba", "bakery",
            "food", "snack", "lunch", "dinner", "breakfast", "chai",
            "dominos", "mcdonalds", "kfc", "subway", "starbucks",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Groceries ───────────────────────────────────────────────────────────
    {
        "category": "Groceries",
        "keywords": [
            "grocery", "supermarket", "bigbasket", "blinkit", "dmart",
            "reliance fresh", "more", "vegetables", "fruits", "milk",
            "kirana", "mart", "store", "provisions", "zepto",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Transport ───────────────────────────────────────────────────────────
    {
        "category": "Transport",
        "keywords": [
            "uber", "ola", "rapido", "auto", "taxi", "bus", "metro",
            "train", "irctc", "fuel", "petrol", "diesel", "parking",
            "toll", "flight", "indigo", "air india", "spicejet",
            "local train", "rickshaw",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Utilities ───────────────────────────────────────────────────────────
    {
        "category": "Utilities",
        "keywords": [
            "electricity", "water bill", "gas", "broadband", "internet",
            "wifi", "recharge", "mobile", "airtel", "jio", "vi ",
            "bsnl", "tata sky", "dth", "cable", "maintenance", "society",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Shopping ────────────────────────────────────────────────────────────
    {
        "category": "Shopping",
        "keywords": [
            "amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa",
            "clothes", "shoes", "fashion", "electronics", "mobile",
            "laptop", "gadget", "watch", "jewellery", "gift",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Health & Medical ────────────────────────────────────────────────────
    {
        "category": "Health & Medical",
        "keywords": [
            "pharmacy", "medical", "hospital", "clinic", "doctor",
            "medicine", "apollo", "1mg", "netmeds", "pharmeasy",
            "gym", "fitness", "yoga", "health",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Entertainment ───────────────────────────────────────────────────────
    {
        "category": "Entertainment",
        "keywords": [
            "netflix", "hotstar", "amazon prime", "spotify", "youtube",
            "movie", "cinema", "pvr", "inox", "bookmyshow", "concert",
            "game", "steam", "play", "subscription",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Education ───────────────────────────────────────────────────────────
    {
        "category": "Education",
        "keywords": [
            "udemy", "coursera", "books", "stationery", "college",
            "fees", "tuition", "school", "exam", "coaching",
            "education", "course", "learning",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Rent & Housing ──────────────────────────────────────────────────────
    {
        "category": "Rent & Housing",
        "keywords": [
            "rent", "landlord", "housing", "flat", "pg ", "hostel",
            "deposit", "lease",
        ],
        "min_amount": None,
        "max_amount": None,
    },
    # ── Finance & Banking ───────────────────────────────────────────────────
    {
        "category": "Finance & Banking",
        "keywords": [
            "emi", "loan", "insurance", "mutual fund", "sip", "investment",
            "fd", "bank", "transfer", "upi", "interest", "credit card",
            "tax", "savings",
        ],
        "min_amount": None,
        "max_amount": None,
    },
]

# ── Prolog-style amount-based override rules ─────────────────────────────────
# category(T, 'Rent & Housing') :- amount(T, A), A > 5000, not(other_rule_matched).
AMOUNT_RULES = [
    {"category": "Rent & Housing",  "min_amount": 5000,  "max_amount": None,   "keywords": []},
    {"category": "Utilities",       "min_amount": 100,   "max_amount": 3000,   "keywords": []},
]


# ---------------------------------------------------------------------------
# PROLOG ENGINE
# ---------------------------------------------------------------------------

class PrologEngine:
    """
    Mimics a Prolog inference engine with a knowledge base of rules.

    Prolog analogy:
        query(Description, Amount, Category) :-
            rule(Keywords, Category),
            member(K, Keywords),
            sub_string(Description, _, _, _, K).   % contains/2
    """

    def __init__(self, rules=None, amount_rules=None):
        self.rules = rules or RULES
        self.amount_rules = amount_rules or AMOUNT_RULES

    def _contains(self, description: str, keyword: str) -> bool:
        """Prolog: contains(Description, Keyword)."""
        return keyword.lower() in description.lower()

    def _keyword_match(self, description: str, keywords: list) -> bool:
        """Prolog: keyword_match(Description, Keywords) :- member(K, Keywords), contains(Description, K)."""
        return any(self._contains(description, k) for k in keywords)

    def _amount_in_range(self, amount: float, min_a, max_a) -> bool:
        """Prolog: amount_in_range(Amount, Min, Max)."""
        if min_a is not None and amount < min_a:
            return False
        if max_a is not None and amount > max_a:
            return False
        return True

    def query(self, description: str, amount: float) -> str:
        """
        Main resolution procedure — equivalent to:
            ?- category(transaction(Description, Amount), Category).

        First-match semantics (Prolog cut on first successful rule).
        """
        # 1. Try keyword-based rules first
        for rule in self.rules:
            if rule["keywords"] and self._keyword_match(description, rule["keywords"]):
                if self._amount_in_range(amount, rule["min_amount"], rule["max_amount"]):
                    return rule["category"]

        # 2. Fall back to amount-based rules (no keywords required)
        for rule in self.amount_rules:
            if not rule["keywords"]:  # pure amount rule
                if self._amount_in_range(amount, rule["min_amount"], rule["max_amount"]):
                    return rule["category"]

        # 3. Default fact: category(_, 'Other')
        return "Other"

    def explain(self, description: str, amount: float) -> str:
        """Returns a human-readable explanation of which rule fired."""
        for i, rule in enumerate(self.rules):
            if rule["keywords"] and self._keyword_match(description, rule["keywords"]):
                if self._amount_in_range(amount, rule["min_amount"], rule["max_amount"]):
                    matched_kw = [k for k in rule["keywords"] if self._contains(description, k)]
                    return (
                        f"Rule #{i+1} fired → category('{rule['category']}')\n"
                        f"  Matched keyword(s): {matched_kw}\n"
                        f"  Amount ₹{amount:.2f} in range [{rule['min_amount']}, {rule['max_amount']}]"
                    )
        for i, rule in enumerate(self.amount_rules):
            if not rule["keywords"]:
                if self._amount_in_range(amount, rule["min_amount"], rule["max_amount"]):
                    return (
                        f"Amount rule #{i+1} fired → category('{rule['category']}')\n"
                        f"  Amount ₹{amount:.2f} in range [{rule['min_amount']}, {rule['max_amount']}]"
                    )
        return "Default rule fired → category('Other')\n  No keyword or amount rule matched."

    def list_rules(self):
        """Pretty-print all Prolog-style rules in the knowledge base."""
        lines = ["\n📚 PROLOG KNOWLEDGE BASE\n" + "="*50]
        lines.append("\n% Keyword-based rules (Horn clauses):")
        for i, rule in enumerate(self.rules):
            kws = ", ".join(rule["keywords"][:5])
            if len(rule["keywords"]) > 5:
                kws += f", ... (+{len(rule['keywords'])-5} more)"
            lines.append(f"  Rule {i+1:02d}: category(T, '{rule['category']}') :- keyword_match(T, [{kws}]).")
        lines.append("\n% Amount-based rules:")
        for i, rule in enumerate(self.amount_rules):
            lines.append(
                f"  Rule {i+1:02d}: category(T, '{rule['category']}') :- "
                f"amount(T, A), A >= {rule['min_amount']}."
            )
        lines.append("\n% Default fact:")
        lines.append("  category(_, 'Other').")
        return "\n".join(lines)
