"""
charts.py
---------
Visualization module — bar charts and pie charts using matplotlib.
"""

import os
import matplotlib
matplotlib.use("Agg")   # non-interactive backend (no display required)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict


# ── Colour palette ─────────────────────────────────────────────────────────
PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
]


def _save(fig, path: str):
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# 1. PIE CHART  — spending share by category
# ---------------------------------------------------------------------------

def pie_chart(category_totals: dict, output_path: str, title: str = "Spending by Category") -> str:
    """
    Generates a pie chart of total spending per category.
    """
    labels = list(category_totals.keys())
    sizes  = list(category_totals.values())
    colors = PALETTE[:len(labels)]

    # Explode the largest slice slightly
    max_idx = sizes.index(max(sizes))
    explode = [0.05 if i == max_idx else 0 for i in range(len(sizes))]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct="%1.1f%%",
        startangle=140,
        explode=explode,
        colors=colors,
        pctdistance=0.82,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    # Legend with amounts
    legend_labels = [f"{l}  ₹{v:,.0f}" for l, v in zip(labels, sizes)]
    ax.legend(
        wedges, legend_labels,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        fontsize=9,
        frameon=False,
    )
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    return _save(fig, output_path)


# ---------------------------------------------------------------------------
# 2. BAR CHART  — spending by category
# ---------------------------------------------------------------------------

def bar_chart(category_totals: dict, output_path: str, title: str = "Expenses by Category") -> str:
    """
    Horizontal bar chart sorted by amount descending.
    """
    sorted_items = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    colors = PALETTE[:len(labels)]

    fig, ax = plt.subplots(figsize=(9, max(4, len(labels) * 0.6 + 1)))
    bars = ax.barh(labels, values, color=colors, edgecolor="white", height=0.6)

    # Value annotations
    for bar, val in zip(bars, values):
        ax.text(
            val + max(values) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"₹{val:,.0f}",
            va="center", ha="left", fontsize=9, color="#333333",
        )

    ax.set_xlabel("Amount (₹)", fontsize=11)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(values) * 1.2)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    return _save(fig, output_path)


# ---------------------------------------------------------------------------
# 3. MONTHLY TREND  — line/bar chart over time
# ---------------------------------------------------------------------------

def monthly_trend_chart(monthly_data: dict, output_path: str, title: str = "Monthly Spending Trend") -> str:
    """
    Bar chart of total spending per month.
    monthly_data = { "Jan 2025": 12000, "Feb 2025": 9500, ... }
    """
    months = list(monthly_data.keys())
    totals = list(monthly_data.values())

    fig, ax = plt.subplots(figsize=(max(6, len(months) * 1.2), 5))
    bars = ax.bar(months, totals, color=PALETTE[0], edgecolor="white", width=0.6)

    for bar, val in zip(bars, totals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(totals) * 0.01,
            f"₹{val:,.0f}",
            ha="center", va="bottom", fontsize=8, color="#333333",
        )

    ax.set_ylabel("Total Spending (₹)", fontsize=11)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xticks(rotation=30, ha="right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    return _save(fig, output_path)


# ---------------------------------------------------------------------------
# 4. STACKED BAR  — category breakdown per month
# ---------------------------------------------------------------------------

def stacked_bar_chart(monthly_category_data: dict, output_path: str,
                      title: str = "Monthly Category Breakdown") -> str:
    """
    monthly_category_data = {
        "Jan 2025": {"Food & Dining": 3000, "Transport": 1200, ...},
        ...
    }
    """
    months = list(monthly_category_data.keys())
    # Collect all categories
    all_cats = sorted(set(
        cat for month_data in monthly_category_data.values() for cat in month_data
    ))
    colors = {cat: PALETTE[i % len(PALETTE)] for i, cat in enumerate(all_cats)}

    fig, ax = plt.subplots(figsize=(max(7, len(months) * 1.4), 5))
    bottom = np.zeros(len(months))

    for cat in all_cats:
        vals = [monthly_category_data[m].get(cat, 0) for m in months]
        ax.bar(months, vals, bottom=bottom, label=cat,
               color=colors[cat], edgecolor="white", width=0.6)
        bottom += np.array(vals)

    ax.set_ylabel("Amount (₹)", fontsize=11)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    plt.xticks(rotation=30, ha="right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    return _save(fig, output_path)
