from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

def generate_monthly_report(profile):
    """
    Generate a monthly financial report PDF
    
    Args:
        profile: User profile dictionary
    
    Returns:
        str: Path to generated PDF file
    """
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Generate filename
    filename = f"monthly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6C63FF'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6C63FF'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("Captain Credo - Monthly Financial Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Key Metrics
    story.append(Paragraph("Key Financial Metrics", heading_style))
    
    # Calculate metrics
    monthly_income = profile.get('monthly_income', 0)
    monthly_expense = profile.get('monthly_expense', 0)
    current_loans = profile.get('current_loans', [])
    total_emi = sum([loan.get('emi', 0) for loan in current_loans])
    monthly_savings = monthly_income - monthly_expense - total_emi
    
    metrics_data = [
        ['Metric', 'Value'],
        ['Credit Score', str(profile.get('credit_score', 0))],
        ['Monthly Income', f'₹{monthly_income:,}'],
        ['Monthly Expenses', f'₹{monthly_expense:,}'],
        ['Total EMI Payments', f'₹{total_emi:,}'],
        ['Monthly Savings', f'₹{monthly_savings:,}'],
        ['Credit Utilization', f"{profile.get('credit_utilization', 0)}%"],
        ['Number of Credit Cards', str(profile.get('num_credit_cards', 0))],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6C63FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Current Loans
    if current_loans:
        story.append(Paragraph("Current Loans", heading_style))
        
        loans_data = [['Loan #', 'Amount', 'Monthly EMI', 'Remaining Tenure (Months)']]
        for i, loan in enumerate(current_loans, 1):
            loans_data.append([
                str(i),
                f'₹{loan.get("amount", 0):,}',
                f'₹{loan.get("emi", 0):,}',
                str(loan.get("remaining_tenure", 0))
            ])
        
        loans_table = Table(loans_data, colWidths=[1*inch, 2*inch, 2*inch, 2.5*inch])
        loans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6C63FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(loans_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    
    recommendations = []
    credit_score = profile.get('credit_score', 0)
    if credit_score < 700:
        recommendations.append("• Work on improving your credit score by paying bills on time and reducing debt")
    
    credit_utilization = profile.get('credit_utilization', 0)
    if credit_utilization > 30:
        recommendations.append(f"• Reduce credit utilization from {credit_utilization}% to below 30%")
    
    if monthly_savings < (monthly_income * 0.1):
        recommendations.append("• Aim to save at least 10-20% of your monthly income")
    
    if total_emi > (monthly_income * 0.3):
        recommendations.append("• Consider consolidating or refinancing loans to reduce monthly payments")
    
    if not recommendations:
        recommendations.append("• Your financial health looks good! Maintain these good habits.")
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("This is a financial advisory report. For professional financial advice, consult a certified financial advisor.", 
                          styles['Italic']))
    
    # Build PDF
    doc.build(story)
    
    return filepath
