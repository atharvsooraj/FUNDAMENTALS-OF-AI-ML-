"""
sample_data.py
--------------
Generates realistic sample expense CSV data for Mumbai-based user.
Run this to create data/expenses.csv for testing.
"""

import csv
import random
import os
from datetime import date, timedelta

TRANSACTIONS = [
    # Food & Dining
    ("Zomato Order - Biryani House", 320),
    ("Swiggy - Pizza delivery", 450),
    ("Cafe Coffee Day", 180),
    ("Restaurant dinner with friends", 1200),
    ("Chai tapri near office", 20),
    ("Dominos online order", 560),
    ("McDonald's breakfast", 210),
    ("Local dhaba lunch", 90),
    # Groceries
    ("BigBasket weekly order", 1800),
    ("D-Mart grocery shopping", 2200),
    ("Blinkit - milk and eggs", 320),
    ("Local kirana store", 450),
    ("Zepto - vegetables", 380),
    # Transport
    ("Uber to airport", 620),
    ("Ola cab - office commute", 180),
    ("Mumbai local train pass", 400),
    ("Petrol - Hero Honda", 900),
    ("Rapido bike taxi", 65),
    ("IRCTC train ticket - Pune", 350),
    # Utilities
    ("Jio monthly recharge", 349),
    ("Electricity bill - MSEDCL", 1200),
    ("Airtel broadband", 799),
    ("Tata Sky DTH recharge", 450),
    ("Society maintenance", 1500),
    # Shopping
    ("Amazon - bluetooth speaker", 1299),
    ("Myntra - summer clothes", 2400),
    ("Flipkart - phone cover", 249),
    ("Nykaa - skincare products", 780),
    # Health
    ("Apollo Pharmacy", 680),
    ("Gym membership fees", 1500),
    ("Doctor consultation fee", 500),
    ("1mg - vitamins order", 420),
    # Entertainment
    ("Netflix subscription", 649),
    ("BookMyShow - movie tickets", 580),
    ("Spotify premium", 119),
    ("Amazon Prime renewal", 1499),
    # Education
    ("Udemy Python course", 399),
    ("Books from Amazon", 750),
    ("Coaching class fees", 2000),
    # Rent
    ("Monthly rent payment", 12000),
    # Finance
    ("LIC premium payment", 5000),
    ("SIP mutual fund", 3000),
    ("Credit card bill payment", 8000),
]


def generate_csv(output_path: str, n_months: int = 3):
    rows = []
    start = date.today() - timedelta(days=n_months * 30)

    for _ in range(80):
        desc, base_amt = random.choice(TRANSACTIONS)
        # Add slight variation to amounts
        amount = round(base_amt * random.uniform(0.85, 1.15), 2)
        txn_date = start + timedelta(days=random.randint(0, n_months * 30))
        rows.append({
            "date": txn_date.strftime("%Y-%m-%d"),
            "description": desc,
            "amount": amount,
        })

    rows.sort(key=lambda x: x["date"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "description", "amount"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Sample data written to {output_path}  ({len(rows)} transactions)")
    return output_path


if __name__ == "__main__":
    generate_csv("data/expenses.csv")
