# 📊 Sales Data Analysis Dashboard

A complete retail sales analytics project built with Python, Pandas, NumPy, and Matplotlib.

# Features
- Monthly revenue & profit trends
- Top-selling product analysis
- Regional sales breakdown
- Category performance & profit margin
- Customer segmentation (RFM Analysis)
- PDF report generation
- Power BI integration guide

# Tech Stack
- **Python** · Pandas · NumPy · Matplotlib
- **Jupyter Notebook** for analysis
- **ReportLab** for PDF export
- **Power BI** for BI dashboard

# Setup
```bash
git clone https://github.com/YOUR_USERNAME/sales-dashboard.git
cd sales-dashboard
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
jupyter notebook sales_analysis.ipynb
```

# Project Structure
sales-dashboard/
├── sales_analysis.ipynb       # Main analysis notebook
├── generate_pdf_report.py     # PDF report generator
├── PowerBI_Setup_Guide.md     # Power BI setup instructions
├── requirements.txt
├── data/
│   └── sales_analysis_export.xlsx
└── charts/                    # Auto-generated chart PNGs

# Dataset
Uses a synthetic retail dataset (Superstore-style).
To use real data: download from [Kaggle Superstore](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
and replace the data generation cell with:
`df = pd.read_csv('Sample - Superstore.csv', encoding='latin-1')`