"""
charts.py — All Matplotlib chart functions. Each returns a Figure object.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Shared style ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#FFFFFF', 'axes.facecolor': '#FFFFFF',
    'axes.edgecolor': '#E8ECF4',   'axes.labelcolor': '#444',
    'xtick.color': '#7B8FA1',      'ytick.color': '#7B8FA1',
    'grid.color': '#F0F4FA',       'grid.linestyle': '--',
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,      'axes.spines.right': False,
})

C = {
    'blue':   '#378ADD', 'green':  '#3B6D11', 'purple': '#7F77DD',
    'amber':  '#EF9F27', 'coral':  '#D85A30', 'pink':   '#D4537E',
    'gray':   '#888780', 'red':    '#E24B4A',
}
REG_COLS = [C['blue'], C['purple'], C['amber'], C['coral'], C['pink'], C['green']]
CAT_COLS = [C['blue'], C['purple'], C['amber'], C['coral'], C['green']]


def _fmt_k(v, _): return f'${v/1000:.0f}K'
def _fmt_pct(v, _): return f'{v:.0f}%'


# ── 1. Monthly trend ───────────────────────────────────────────────────────────
def chart_trend(monthly):
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), height_ratios=[3, 1])
    fig.suptitle('Monthly Revenue & Profit', fontsize=14, fontweight='bold', y=0.99, color='#1A1A2E')

    x = range(len(monthly))
    ax = axes[0]
    ax.fill_between(x, monthly['revenue'], alpha=0.10, color=C['blue'])
    ax.plot(x, monthly['revenue'], color=C['blue'], lw=2.5, marker='o', ms=5, label='Revenue')
    ax.fill_between(x, monthly['profit'],  alpha=0.10, color=C['green'])
    ax.plot(x, monthly['profit'],  color=C['green'], lw=2.5, marker='s', ms=5, ls='--', label='Profit')
    ax.set_xticks(x); ax.set_xticklabels(monthly['month_name'], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_k))
    ax.legend(frameon=False, fontsize=10); ax.grid(True, axis='y', alpha=0.6)

    growth = monthly['revenue_growth'].fillna(0)
    axes[1].bar(x, growth, color=[C['green'] if v >= 0 else C['red'] for v in growth], alpha=0.8, width=0.6)
    axes[1].axhline(0, color='#ccc', lw=0.8)
    axes[1].set_xticks(x); axes[1].set_xticklabels(monthly['month_name'], fontsize=9)
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_pct))
    axes[1].set_title('Month-over-month growth', fontsize=9, pad=4, color='#7B8FA1')
    axes[1].grid(True, axis='y', alpha=0.4)

    plt.tight_layout()
    return fig


# ── 2. Top products ────────────────────────────────────────────────────────────
def chart_products(prod):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Top Products Analysis', fontsize=13, fontweight='bold', color='#1A1A2E')

    bars = ax1.barh(prod['product'], prod['revenue'] / 1000, color=C['blue'], alpha=0.85)
    ax1.set_xlabel('Revenue ($K)', fontsize=9)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(_fmt_k))
    ax1.set_title('Revenue by product', fontsize=11)
    for bar, val in zip(bars, prod['revenue']):
        ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                 f'${val/1000:.0f}K', va='center', fontsize=8, color='#444')

    sc = ax2.scatter(prod['revenue'] / 1000, prod['margin_pct'],
                     s=60, c=prod['profit'] / 1000, cmap='YlGn',
                     alpha=0.85, edgecolors='#333', lw=0.5)
    plt.colorbar(sc, ax=ax2, label='Profit ($K)')
    ax2.set_xlabel('Revenue ($K)', fontsize=9)
    ax2.set_ylabel('Profit margin (%)', fontsize=9)
    ax2.set_title('Revenue vs margin', fontsize=11)
    for _, row in prod.iterrows():
        ax2.annotate(row['product'].split()[0], (row['revenue'] / 1000, row['margin_pct']),
                     fontsize=8, ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')

    plt.tight_layout()
    return fig


# ── 3. Regional ────────────────────────────────────────────────────────────────
def chart_regional(reg):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle('Regional Sales Analysis', fontsize=13, fontweight='bold', color='#1A1A2E')

    colors = REG_COLS[:len(reg)]
    wedges, texts, autotexts = ax1.pie(
        reg['revenue'], labels=reg['region'], autopct='%1.1f%%',
        colors=colors, startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.55, edgecolor='white', lw=2)
    )
    for at in autotexts: at.set_fontsize(10); at.set_fontweight('bold')
    ax1.set_title('Revenue share', fontsize=11)

    x = np.arange(len(reg)); w = 0.35
    ax2.bar(x - w/2, reg['revenue'] / 1000, w, color=C['blue'],  label='Revenue', alpha=0.85)
    ax2.bar(x + w/2, reg['profit']  / 1000, w, color=C['green'], label='Profit',  alpha=0.85)
    ax2.set_xticks(x); ax2.set_xticklabels(reg['region'], fontsize=9)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_k))
    ax2.set_title('Revenue vs profit', fontsize=11)
    ax2.legend(frameon=False, fontsize=9); ax2.grid(True, axis='y', alpha=0.4)

    plt.tight_layout()
    return fig


# ── 4. Category ────────────────────────────────────────────────────────────────
def chart_category(cat, df_raw):
    import pandas as pd
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Category Performance', fontsize=13, fontweight='bold', color='#1A1A2E')

    x = range(len(cat))
    colors = CAT_COLS[:len(cat)]

    # Stacked
    axes[0].bar(x, cat['profit']  / 1000, color=C['green'], label='Profit', alpha=0.9)
    axes[0].bar(x, (cat['revenue'] - cat['profit']) / 1000,
                bottom=cat['profit'] / 1000, color=C['blue'], label='Cost', alpha=0.7)
    axes[0].set_xticks(x); axes[0].set_xticklabels(cat['category'], rotation=20, ha='right', fontsize=8)
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_k))
    axes[0].set_title('Revenue breakdown', fontsize=10)
    axes[0].legend(frameon=False, fontsize=9); axes[0].grid(True, axis='y', alpha=0.4)

    # Margin bars
    bars = axes[1].bar(x, cat['margin'], color=colors, alpha=0.85, width=0.6)
    axes[1].set_xticks(x); axes[1].set_xticklabels(cat['category'], rotation=20, ha='right', fontsize=8)
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_pct))
    axes[1].axhline(cat['margin'].mean(), color='red', ls='--', lw=1, alpha=0.6)
    axes[1].set_title('Profit margin', fontsize=10)
    for bar, val in zip(bars, cat['margin']):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'{val:.1f}%', ha='center', fontsize=8, fontweight='bold')

    # Heatmap
    try:
        pivot = df_raw.pivot_table(values='revenue', index='category', columns='quarter', aggfunc='sum')
        pivot.columns = ['Q1', 'Q2', 'Q3', 'Q4'][:len(pivot.columns)]
        norm = pivot.div(pivot.max(axis=1), axis=0)
        axes[2].imshow(norm.values, cmap='Blues', aspect='auto')
        axes[2].set_xticks(range(len(pivot.columns))); axes[2].set_xticklabels(pivot.columns)
        axes[2].set_yticks(range(len(pivot))); axes[2].set_yticklabels(pivot.index, fontsize=8)
        axes[2].set_title('Seasonal heatmap', fontsize=10)
        for i in range(len(pivot)):
            for j in range(len(pivot.columns)):
                axes[2].text(j, i, f'${pivot.iloc[i,j]/1000:.0f}K',
                             ha='center', va='center', fontsize=7,
                             color='white' if norm.iloc[i,j] > 0.7 else '#333')
    except Exception:
        axes[2].text(0.5, 0.5, 'Not enough quarterly data', ha='center', va='center', transform=axes[2].transAxes)

    plt.tight_layout()
    return fig


# ── 5. Customer segments ───────────────────────────────────────────────────────
def chart_segments(seg):
    seg_colors = {
        'Champions': C['blue'], 'Loyal Customers': C['purple'],
        'At-Risk': C['red'],    'Potential Loyalists': C['amber'],
        'New Customers': C['green'], 'Hibernating': C['gray']
    }
    colors = [seg_colors.get(s, C['gray']) for s in seg['segment']]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle('Customer Segmentation — RFM', fontsize=13, fontweight='bold', color='#1A1A2E')

    ax1.pie(seg['count'], labels=seg['segment'], autopct='%1.1f%%',
            colors=colors, startangle=90, pctdistance=0.75,
            wedgeprops=dict(width=0.55, edgecolor='white', lw=2))
    ax1.set_title('Customer distribution', fontsize=11)

    seg_s  = seg.sort_values('avg_monetary', ascending=True)
    bc     = [seg_colors.get(s, C['gray']) for s in seg_s['segment']]
    bars   = ax2.barh(seg_s['segment'], seg_s['avg_monetary'], color=bc, alpha=0.85)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'${v:.0f}'))
    ax2.set_title('Avg revenue per customer', fontsize=11)
    for bar, val in zip(bars, seg_s['avg_monetary']):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                 f'${val:.0f}', va='center', fontsize=9)

    plt.tight_layout()
    return fig
