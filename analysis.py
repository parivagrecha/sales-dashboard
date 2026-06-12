"""
analysis.py — All data processing, KPI calculation, and RFM logic.
Auto-detects column names from any file — no manual mapping needed.
"""

import pandas as pd
import numpy as np

# ── Column name aliases — add more here if needed ──────────────────────────────
DATE_ALIASES     = ['date', 'order_date', 'orderdate', 'order date', 'sale_date',
                    'transaction_date', 'invoice_date', 'purchase_date', 'orderdate']
REVENUE_ALIASES  = ['totalprice', 'total_price', 'total price', 'revenue', 'sales',
                    'sale_amount', 'amount', 'total_amount', 'total_sales', 'netsales',
                    'net_sales', 'gross_sales', 'order_total', 'total', 'price']
PROFIT_ALIASES   = ['profit', 'net_profit', 'profit_amount', 'earnings', 'margin_amount']
CATEGORY_ALIASES = ['category', 'cat', 'product_category', 'item_category', 'type',
                    'product_type', 'department', 'producttype']
REGION_ALIASES   = ['region', 'area', 'zone', 'territory', 'storelocation',
                    'store_location', 'store', 'state', 'city', 'location']
PRODUCT_ALIASES  = ['product', 'product_name', 'item', 'item_name', 'sku',
                    'description', 'goods', 'productname']
CUSTOMER_ALIASES = ['customer_id', 'customerid', 'customer_name', 'customername',
                    'customer', 'client', 'client_id', 'orderid', 'order_id']

def _find_col(df_cols, aliases):
    """Find first matching column, case-insensitive."""
    lower_map = {c.lower().strip(): c for c in df_cols}
    for alias in aliases:
        if alias.lower() in lower_map:
            return lower_map[alias.lower()]
    return None


# ── Sample data generator ──────────────────────────────────────────────────────
def generate_sample_data():
    np.random.seed(42)
    n = 5000
    categories = ['Electronics', 'Apparel', 'Home & Garden', 'Sports', 'Kitchen']
    regions    = ['North', 'South', 'East', 'West']
    products = {
        'Electronics':    ['Laptop 15"', 'Wireless Earbuds', 'Smart Watch', 'Tablet Pro', 'Bluetooth Speaker'],
        'Apparel':        ['Running Shoes', 'Winter Jacket', 'Sports T-Shirt', 'Denim Jeans', 'Yoga Pants'],
        'Home & Garden':  ['Office Chair', 'Standing Desk', 'LED Floor Lamp', 'Bookshelf', 'Wall Art Set'],
        'Sports':         ['Yoga Mat', 'Resistance Bands', 'Dumbbell Set', 'Foam Roller', 'Jump Rope'],
        'Kitchen':        ['Blender Pro', 'Air Fryer', 'Coffee Maker', 'Knife Set', 'Food Processor'],
    }

    cat_arr    = np.random.choice(categories, n, p=[0.25, 0.20, 0.16, 0.22, 0.17])
    region_arr = np.random.choice(regions,    n, p=[0.30, 0.26, 0.24, 0.20])
    dates      = pd.date_range('2023-01-01', '2023-12-31', periods=n)
    dates      = dates[np.random.randint(0, len(dates), n)]

    base_price  = {'Electronics': 350, 'Apparel': 80, 'Home & Garden': 200, 'Sports': 55, 'Kitchen': 120}
    revenue_arr = np.array([base_price[c] * np.random.uniform(0.7, 2.5) for c in cat_arr])
    month_mult  = {1:0.85, 2:0.80, 3:0.95, 4:1.00, 5:0.92, 6:1.08,
                   7:1.18, 8:1.12, 9:1.10, 10:1.25, 11:1.42, 12:1.35}
    revenue_arr *= np.array([month_mult[d.month] for d in dates])

    margin      = {'Electronics': 0.22, 'Apparel': 0.35, 'Home & Garden': 0.28, 'Sports': 0.40, 'Kitchen': 0.30}
    profit_arr  = np.array([revenue_arr[i] * margin[cat_arr[i]] * np.random.uniform(0.75, 1.25) for i in range(n)])
    product_arr = [np.random.choice(products[c]) for c in cat_arr]

    df = pd.DataFrame({
        'order_date':  pd.to_datetime(dates),
        'customer_id': [f'CUST{str(i).zfill(4)}' for i in np.random.randint(1, 800, n)],
        'category':    cat_arr,
        'product':     product_arr,
        'region':      region_arr,
        'revenue':     revenue_arr.round(2),
        'profit':      profit_arr.round(2),
        'quantity':    np.random.randint(1, 8, n),
    })
    df['month']   = df['order_date'].dt.month
    df['quarter'] = df['order_date'].dt.quarter
    return df


# ── Prepare uploaded data — fully auto-detects columns ────────────────────────
def prepare_data(df, col_map=None):
    """
    Auto-detects all columns by name matching.
    col_map from sidebar is used only as a hint — auto-detection always runs first.
    """
    cols = df.columns.tolist()

    # ── Auto-detect each column ────────────────────────────────────────────────
    date_col     = _find_col(cols, DATE_ALIASES)
    revenue_col  = _find_col(cols, REVENUE_ALIASES)
    profit_col   = _find_col(cols, PROFIT_ALIASES)
    category_col = _find_col(cols, CATEGORY_ALIASES)
    region_col   = _find_col(cols, REGION_ALIASES)
    product_col  = _find_col(cols, PRODUCT_ALIASES)
    customer_col = _find_col(cols, CUSTOMER_ALIASES)

    # ── Use sidebar hints only if auto-detect failed ───────────────────────────
    if col_map:
        if not date_col     and col_map.get('date')     in cols: date_col     = col_map['date']
        if not revenue_col  and col_map.get('revenue')  in cols: revenue_col  = col_map['revenue']
        if not profit_col   and col_map.get('profit')   in cols: profit_col   = col_map['profit']
        if not category_col and col_map.get('category') in cols: category_col = col_map['category']
        if not region_col   and col_map.get('region')   in cols: region_col   = col_map['region']
        if not product_col  and col_map.get('product')  in cols: product_col  = col_map['product']
        if not customer_col and col_map.get('customer') in cols: customer_col = col_map['customer']

    # ── Date column is required ────────────────────────────────────────────────
    if not date_col:
        raise ValueError(
            f"No date column found. Your file has: {cols}. "
            "Please set the 'Date column' in the sidebar."
        )

    # ── Revenue column is required ─────────────────────────────────────────────
    if not revenue_col:
        raise ValueError(
            f"No revenue/sales column found. Your file has: {cols}. "
            "Please set the 'Revenue column' in the sidebar."
        )

    # ── Build rename dict ──────────────────────────────────────────────────────
    rename = {date_col: 'order_date', revenue_col: 'revenue'}
    if profit_col:   rename[profit_col]   = 'profit'
    if category_col: rename[category_col] = 'category'
    if region_col:   rename[region_col]   = 'region'
    if product_col:  rename[product_col]  = 'product'
    if customer_col: rename[customer_col] = 'customer_id'

    df = df.rename(columns=rename)

    # ── Parse & clean date ─────────────────────────────────────────────────────
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    before = len(df)
    df = df.dropna(subset=['order_date'])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  Dropped {dropped} rows with invalid dates.")

    # ── Numeric revenue / profit ───────────────────────────────────────────────
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)

    if 'profit' not in df.columns:
        # Estimate profit as 25% of revenue if no profit column
        df['profit'] = df['revenue'] * 0.25
    else:
        df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(df['revenue'] * 0.25)

    # ── Categorical defaults ───────────────────────────────────────────────────
    for col, default in [('category', 'General'), ('region', 'Unknown'),
                         ('product', 'Unknown'), ('customer_id', 'UNKNOWN')]:
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default).astype(str).str.strip()

    # ── Derived columns ────────────────────────────────────────────────────────
    df['month']   = df['order_date'].dt.month
    df['quarter'] = df['order_date'].dt.quarter

    return df


# ── KPI computation ────────────────────────────────────────────────────────────
def compute_kpis(df):
    rev    = df['revenue'].sum()
    profit = df['profit'].sum()
    orders = len(df)
    aov    = df['revenue'].mean()
    margin = (profit / rev * 100) if rev > 0 else 0

    def fmt(v):
        if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
        if v >= 1_000:     return f"${v/1_000:.1f}K"
        return f"${v:.0f}"

    return {
        'revenue': fmt(rev),
        'profit':  fmt(profit),
        'orders':  f"{orders:,}",
        'aov':     f"${aov:.0f}",
        'margin':  f"{margin:.1f}%",
        '_rev_raw':    rev,
        '_profit_raw': profit,
        '_orders_raw': orders,
        '_margin_raw': margin,
    }


# ── Monthly trend ──────────────────────────────────────────────────────────────
def monthly_trend(df):
    monthly = df.groupby('month').agg(
        revenue=('revenue', 'sum'),
        profit=('profit',   'sum'),
        orders=('revenue',  'count')
    ).reset_index()
    monthly['month_name']     = pd.to_datetime(monthly['month'], format='%m').dt.strftime('%b')
    monthly['revenue_growth'] = monthly['revenue'].pct_change() * 100
    return monthly


# ── Top products ───────────────────────────────────────────────────────────────
def top_products(df, n=8):
    agg = {'revenue': ('revenue', 'sum'), 'profit': ('profit', 'sum'), 'orders': ('revenue', 'count')}
    if 'quantity' in df.columns:
        agg['units'] = ('quantity', 'sum')
    prod = df.groupby('product').agg(**agg).sort_values('revenue', ascending=False).head(n).reset_index()
    if 'units' not in prod.columns:
        prod['units'] = prod['orders']
    prod['margin_pct'] = (prod['profit'] / prod['revenue'] * 100).round(1)
    return prod


# ── Regional analysis ──────────────────────────────────────────────────────────
def regional_analysis(df):
    reg = df.groupby('region').agg(
        revenue=('revenue', 'sum'),
        profit=('profit',   'sum'),
        orders=('revenue',  'count')
    ).reset_index()
    reg['margin']    = (reg['profit'] / reg['revenue'] * 100).round(1)
    reg['rev_share'] = (reg['revenue'] / reg['revenue'].sum() * 100).round(1)
    return reg.sort_values('revenue', ascending=False)


# ── Category analysis ──────────────────────────────────────────────────────────
def category_analysis(df):
    cat = df.groupby('category').agg(
        revenue=('revenue', 'sum'),
        profit=('profit',   'sum'),
        orders=('revenue',  'count')
    ).reset_index()
    cat['margin'] = (cat['profit'] / cat['revenue'] * 100).round(1)
    return cat.sort_values('revenue', ascending=False)


# ── RFM segmentation ───────────────────────────────────────────────────────────
def rfm_segmentation(df):
    snapshot = df['order_date'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('customer_id').agg(
        recency=('order_date',  lambda x: (snapshot - x.max()).days),
        frequency=('order_date','count'),
        monetary=('revenue',    'sum')
    ).reset_index()

    try:
        rfm['r_score'] = pd.qcut(rfm['recency'],   5, labels=[5,4,3,2,1], duplicates='drop').astype(int)
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop').astype(int)
        rfm['m_score'] = pd.qcut(rfm['monetary'],  5, labels=[1,2,3,4,5], duplicates='drop').astype(int)
    except Exception:
        rfm['r_score'] = 3
        rfm['f_score'] = 3
        rfm['m_score'] = 3

    def segment(row):
        r, f = row['r_score'], row['f_score']
        if r >= 4 and f >= 4: return 'Champions'
        if r >= 3 and f >= 3: return 'Loyal Customers'
        if r >= 4 and f <= 2: return 'Potential Loyalists'
        if r <= 2 and f >= 3: return 'At-Risk'
        if r == 5 and f == 1: return 'New Customers'
        return 'Hibernating'

    rfm['segment'] = rfm.apply(segment, axis=1)

    seg = rfm.groupby('segment').agg(
        count=('customer_id',   'count'),
        avg_recency=('recency',    'mean'),
        avg_frequency=('frequency','mean'),
        avg_monetary=('monetary',  'mean')
    ).round(1).reset_index()
    seg['pct'] = (seg['count'] / seg['count'].sum() * 100).round(1)

    return rfm, seg