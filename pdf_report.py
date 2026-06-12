"""
pdf_report.py — Generates a PDF report in memory and returns bytes.
"""

import io, os, tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from charts import chart_trend, chart_products, chart_regional, chart_category, chart_segments

C_BLUE  = colors.HexColor('#378ADD')
C_GREEN = colors.HexColor('#3B6D11')
C_DARK  = colors.HexColor('#1A1A2E')
C_GRAY  = colors.HexColor('#888780')
C_LGRAY = colors.HexColor('#F5F5F5')

def S(name, **kw):
    styles = getSampleStyleSheet()
    base = styles.get(name, styles['Normal'])
    return ParagraphStyle(f'_s{id(kw)}', parent=base, **kw)

def _save_fig(fig):
    buf = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    fig.savefig(buf.name, dpi=130, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return buf.name

def _img(path, w=165, h=80):
    return Image(path, width=w*mm, height=h*mm)

def _section(story, num, title):
    badge = Table([[Paragraph(str(num), S('Normal', fontSize=11, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER))]],
                  colWidths=[9*mm])
    badge.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),C_BLUE),
                                ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
                                ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
    row = Table([[badge, Paragraph(title, S('Normal', fontSize=14, fontName='Helvetica-Bold', textColor=C_DARK))]],
                colWidths=[12*mm, 152*mm])
    row.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),0)]))
    story.append(row)
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#DDDDDD'), spaceAfter=6))

def _finding(story, text):
    t = Table([[Paragraph(f'Key finding: {text}',
                           S('Normal', fontSize=9, fontName='Helvetica-Oblique', textColor=C_DARK, leading=14, leftIndent=4))]],
              colWidths=[165*mm])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#EEF5FF')),
                            ('LEFTPADDING',(0,0),(-1,-1),10),
                            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t)
    story.append(Spacer(1, 4*mm))


def generate_pdf(df, monthly_df, prod_df, reg_df, cat_df, seg_df, kpis, source):
    """Generate full PDF report, return bytes."""
    tmp_files = []

    # Save all charts to temp files
    fig1 = chart_trend(monthly_df);          p1 = _save_fig(fig1); tmp_files.append(p1)
    fig2 = chart_products(prod_df);          p2 = _save_fig(fig2); tmp_files.append(p2)
    fig3 = chart_regional(reg_df);           p3 = _save_fig(fig3); tmp_files.append(p3)
    fig4 = chart_category(cat_df, df);       p4 = _save_fig(fig4); tmp_files.append(p4)
    fig5 = chart_segments(seg_df);           p5 = _save_fig(fig5); tmp_files.append(p5)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=18*mm, rightMargin=18*mm,
                             topMargin=15*mm, bottomMargin=15*mm)
    story = []
    body_s = S('Normal', fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#444'), leading=16, spaceAfter=8)

    # ── Cover ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 25*mm))
    story.append(Paragraph('Sales Data Analysis Report',
                            S('Normal', fontSize=24, fontName='Helvetica-Bold', textColor=C_DARK, alignment=TA_CENTER, spaceAfter=10)))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(source,
                            S('Normal', fontSize=10, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=16)))
    story.append(Spacer(1, 6*mm))
    
    kpi_val_s = S('Normal', fontSize=18, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER, spaceBefore=6)
    kpi_lbl_s = S('Normal', fontSize=9,  fontName='Helvetica', textColor=colors.HexColor('#AACCEE'), alignment=TA_CENTER, spaceAfter=6)
    kpi_banner = Table(
        [[Paragraph(v, kpi_val_s) for v in [kpis['revenue'], kpis['profit'], kpis['orders'], kpis['margin']]],
         [Paragraph(l, kpi_lbl_s) for l in ['Total Revenue', 'Net Profit', 'Orders', 'Profit Margin']]],
        colWidths=[41*mm]*4
    )
    kpi_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_DARK),
        ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(kpi_banner)
    story.append(PageBreak())

    # ── Section 1: Monthly ─────────────────────────────────────────────────────
    _section(story, 1, 'Monthly Revenue & Profit Trends')
    story.append(_img(p1, 165, 85))
    story.append(Paragraph('Figure 1: Monthly revenue and profit with month-over-month growth.',
                            S('Normal', fontSize=8, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=8)))
    peak = monthly_df.loc[monthly_df['revenue'].idxmax(), 'month_name']
    _finding(story, f'Peak revenue month is {peak}. Q4 (Oct–Dec) typically accounts for 30–35% of annual revenue.')
    story.append(PageBreak())

    # ── Section 2: Products ────────────────────────────────────────────────────
    _section(story, 2, 'Top-Selling Products')
    story.append(_img(p2, 165, 78))
    story.append(Paragraph('Figure 2: Top products by revenue (left) and profit margin bubble chart (right).',
                            S('Normal', fontSize=8, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=8)))
    _finding(story, f'Top product: {prod_df.iloc[0]["product"]} (${prod_df.iloc[0]["revenue"]/1000:.0f}K revenue). '
                    f'Best margin: {prod_df.loc[prod_df["margin_pct"].idxmax(), "product"]} ({prod_df["margin_pct"].max():.1f}%).')
    story.append(PageBreak())

    # ── Section 3: Regional ────────────────────────────────────────────────────
    _section(story, 3, 'Regional Sales Analysis')
    story.append(_img(p3, 165, 78))
    story.append(Paragraph('Figure 3: Regional revenue share and revenue vs profit comparison.',
                            S('Normal', fontSize=8, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=8)))
    top_reg = reg_df.iloc[0]
    _finding(story, f'{top_reg["region"]} leads with {top_reg["rev_share"]:.1f}% of total revenue (${top_reg["revenue"]/1000:.0f}K).')
    story.append(PageBreak())

    # ── Section 4: Category ────────────────────────────────────────────────────
    _section(story, 4, 'Category Performance & Profit')
    story.append(_img(p4, 165, 78))
    story.append(Paragraph('Figure 4: Category revenue breakdown, profit margins, and seasonal heatmap.',
                            S('Normal', fontSize=8, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=8)))
    best_m = cat_df.loc[cat_df['margin'].idxmax()]
    _finding(story, f'{best_m["category"]} delivers the highest profit margin at {best_m["margin"]:.1f}%.')
    story.append(PageBreak())

    # ── Section 5: Segments ────────────────────────────────────────────────────
    _section(story, 5, 'Customer Segmentation — RFM')
    story.append(_img(p5, 165, 78))
    story.append(Paragraph('Figure 5: Customer segment distribution and average revenue per segment.',
                            S('Normal', fontSize=8, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=8)))
    _finding(story, 'Champions + Loyal Customers represent high-value retention targets. At-Risk segment needs win-back campaigns.')

    # Segment table
    hdr_s = S('Normal', fontSize=9, fontName='Helvetica-Bold', textColor=colors.white)
    tbl_data = [[Paragraph(h, hdr_s) for h in ['Segment', '% Customers', 'Avg Revenue', 'Avg Orders', 'Action']]]
    actions = {'Champions':'Reward & upsell', 'Loyal Customers':'Loyalty program',
               'Potential Loyalists':'Onboarding offers', 'At-Risk':'Win-back campaign',
               'New Customers':'Nurture sequence', 'Hibernating':'Re-engagement deal'}
    cell_s = S('Normal', fontSize=9, fontName='Helvetica', textColor=C_DARK, alignment=TA_CENTER)
    for _, row in seg_df.iterrows():
        tbl_data.append([
            Paragraph(row['segment'], cell_s),
            Paragraph(f'{row["pct"]:.1f}%', cell_s),
            Paragraph(f'${row["avg_monetary"]:.0f}', cell_s),
            Paragraph(f'{row["avg_frequency"]:.1f}', cell_s),
            Paragraph(actions.get(row['segment'], '—'), cell_s),
        ])
    seg_tbl = Table(tbl_data, colWidths=[45*mm, 32*mm, 32*mm, 28*mm, 38*mm])
    seg_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), C_DARK),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, C_LGRAY]),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#E0E0E0')),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(seg_tbl)

    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#DDDDDD'), spaceAfter=5))
    story.append(Paragraph('Generated with Python · Pandas · Matplotlib · ReportLab · Streamlit',
                            S('Normal', fontSize=8, fontName='Helvetica', textColor=C_GRAY, alignment=TA_CENTER)))

    doc.build(story)

    # Clean up temp chart files
    for f in tmp_files:
        try: os.unlink(f)
        except: pass

    return buf.getvalue()
