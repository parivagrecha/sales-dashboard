"""
Sales Data Analysis — PDF Report Generator
==========================================
Run this AFTER sales_analysis.ipynb (which saves chart_*.png files).

Usage:
    python generate_pdf_report.py

Output:
    Sales_Analysis_Report.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

# ── Color palette ──────────────────────────────────────────────────────────────
C_BLUE   = colors.HexColor('#378ADD')
C_GREEN  = colors.HexColor('#3B6D11')
C_DARK   = colors.HexColor('#1A1A2E')
C_GRAY   = colors.HexColor('#888780')
C_LGRAY  = colors.HexColor('#F5F5F5')
C_WHITE  = colors.white

def S(parent_name, **kw):
    styles = getSampleStyleSheet()
    base = styles.get(parent_name, styles['Normal'])
    return ParagraphStyle(f'_custom_{id(kw)}', parent=base, **kw)

doc = SimpleDocTemplate(
    'Sales_Analysis_Report.pdf', pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=15*mm, bottomMargin=15*mm,
)

story = []

# ── Cover ──────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 30*mm))
story.append(Paragraph('Sales Data Analysis Report', S('Normal', fontSize=28, fontName='Helvetica-Bold', textColor=C_DARK, alignment=TA_CENTER)))
story.append(Paragraph('Retail Performance Intelligence · FY 2023', S('Normal', fontSize=13, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=20)))

# KPI banner
kpi_val_s = S('Normal', fontSize=20, fontName='Helvetica-Bold', textColor=C_WHITE, alignment=TA_CENTER, spaceBefore=6)
kpi_lbl_s = S('Normal', fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#CCDDFF'), alignment=TA_CENTER, spaceAfter=6)
kpi = Table(
    [[Paragraph(v, kpi_val_s) for v in ['$1.47M', '$392.6K', '5,000', '26.8%']],
     [Paragraph(l, kpi_lbl_s) for l in ['Total Revenue', 'Net Profit', 'Orders', 'Profit Margin']]],
    colWidths=[41*mm]*4
)
kpi.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), C_DARK),
    ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
]))
story.append(kpi)
story.append(PageBreak())

# ── Helper functions ────────────────────────────────────────────────────────────
def section_header(num, title):
    badge = Table([[Paragraph(str(num), S('Normal', fontSize=12, fontName='Helvetica-Bold', textColor=C_WHITE, alignment=TA_CENTER))]], colWidths=[9*mm])
    badge.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),C_BLUE),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
    row = Table([[badge, Paragraph(title, S('Normal', fontSize=15, fontName='Helvetica-Bold', textColor=C_DARK))]], colWidths=[12*mm, 152*mm])
    row.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),0)]))
    story.append(row)
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#DDDDDD'), spaceAfter=6))

def add_chart(path, caption, w=165, h=85):
    if os.path.exists(path):
        story.append(Image(path, width=w*mm, height=h*mm))
        story.append(Paragraph(caption, S('Normal', fontSize=9, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=10)))

def key_finding(text):
    kf = Table([[Paragraph(f'Key finding: {text}', S('Normal', fontSize=10, fontName='Helvetica-Oblique', textColor=C_DARK, leading=15, leftIndent=4))]], colWidths=[165*mm])
    kf.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#EEF5FF')),('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(kf)
    story.append(Spacer(1, 4*mm))

body_s = S('Normal', fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#444'), leading=16, spaceAfter=8)

# ── Sections ────────────────────────────────────────────────────────────────────
section_header(1, 'Monthly Revenue & Profit Trends')
add_chart('chart_trend.png', 'Figure 1: Monthly revenue and profit with MoM growth', 165, 88)
key_finding('Revenue peaks in November and December, driven by holiday shopping. Q4 accounts for ~35% of annual revenue.')
story.append(Paragraph('Strong seasonal patterns are evident. February records the lowest monthly revenue while the Q2–Q4 trajectory reflects effective promotional strategies and a growing customer base.', body_s))
story.append(PageBreak())

section_header(2, 'Top-Selling Products')
add_chart('chart_products.png', 'Figure 2: Top 8 products by revenue and margin bubble chart', 165, 80)
key_finding('Running Shoes leads revenue. Winter Jacket delivers the best profit margin despite lower revenue rank.')
story.append(PageBreak())

section_header(3, 'Regional Sales Analysis')
add_chart('chart_regional.png', 'Figure 3: Regional revenue share, revenue vs profit, and monthly trends', 165, 85)
key_finding('North region contributes ~30% of total revenue. Q4 growth is consistent nationwide.')
story.append(PageBreak())

section_header(4, 'Category Performance & Profit')
add_chart('chart_category.png', 'Figure 4: Category breakdown, profit margin bars, and seasonal heatmap', 165, 80)
key_finding('Sports category delivers ~40% profit margin. Electronics leads revenue on thinner 22% margins.')
story.append(PageBreak())

section_header(5, 'Customer Segmentation — RFM Analysis')
add_chart('chart_segments.png', 'Figure 5: Customer segment distribution and avg revenue per segment', 165, 80)
key_finding('Champions + Loyal Customers = ~40% of customers, driving disproportionate revenue. At-Risk segment is a key retention opportunity.')
story.append(PageBreak())

section_header(6, 'Power BI DAX Measures Reference')
dax_measures = [
    ('Total Revenue',       "SUM('Raw Data'[revenue])"),
    ('Total Profit',        "SUM('Raw Data'[profit])"),
    ('Profit Margin %',     "DIVIDE([Total Profit], [Total Revenue], 0) * 100"),
    ('Order Count',         "COUNTROWS('Raw Data')"),
    ('Avg Order Value',     "AVERAGEX('Raw Data', 'Raw Data'[revenue])"),
    ('Revenue Growth MoM',  "VAR curr = [Total Revenue]\nVAR prev = CALCULATE([Total Revenue], DATEADD('Date'[Date],-1,MONTH))\nRETURN DIVIDE(curr - prev, prev, 0)"),
    ('YTD Revenue',         "TOTALYTD([Total Revenue], 'Date'[Date])"),
]
hdr_s = S('Normal', fontSize=9, fontName='Helvetica-Bold', textColor=C_WHITE)
dax_rows = [[Paragraph('Measure Name', hdr_s), Paragraph('DAX Formula', hdr_s)]]
for name, formula in dax_measures:
    dax_rows.append([
        Paragraph(name, S('Normal', fontSize=9, fontName='Helvetica-Bold', textColor=C_BLUE)),
        Paragraph(formula, S('Normal', fontSize=8, fontName='Courier', textColor=C_DARK, leading=12)),
    ])
dax_tbl = Table(dax_rows, colWidths=[55*mm, 110*mm])
dax_tbl.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),C_DARK),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_WHITE, C_LGRAY]),
    ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#E0E0E0')),
    ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
    ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
    ('VALIGN',(0,0),(-1,-1),'TOP'),
]))
story.append(dax_tbl)
story.append(Spacer(1, 6*mm))
story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#DDDDDD'), spaceAfter=5))
story.append(Paragraph('Generated with Python · reportlab · matplotlib · pandas · numpy | Connect sales_analysis_export.xlsx to Power BI as data source', S('Normal', fontSize=8, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER)))

doc.build(story)
print("✅ Sales_Analysis_Report.pdf generated!")
