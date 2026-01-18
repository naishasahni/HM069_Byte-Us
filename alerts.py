from datetime import datetime, timedelta
from utils.data_handler import load_alerts, save_alerts

def generate_alerts(profile):
    """
    Generate alerts based on user profile
    
    Args:
        profile: User profile dictionary
    
    Returns:
        list: List of alert dictionaries
    """
    alerts = []
    
    # Check credit score
    credit_score = profile.get('credit_score', 0)
    if credit_score < 600:
        alerts.append({
            "type": "error",
            "message": f"Your credit score ({credit_score}) is below 600. Consider improving your credit health.",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    elif credit_score < 700:
        alerts.append({
            "type": "warning",
            "message": f"Your credit score ({credit_score}) is moderate. Work on improving it for better loan terms.",
            "priority": "medium",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    
    # Check credit utilization
    credit_utilization = profile.get('credit_utilization', 0)
    if credit_utilization > 60:
        alerts.append({
            "type": "error",
            "message": f"High credit utilization ({credit_utilization}%). Try to keep it below 30% for better credit health.",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    elif credit_utilization > 30:
        alerts.append({
            "type": "warning",
            "message": f"Credit utilization ({credit_utilization}%) is above recommended 30%. Consider reducing it.",
            "priority": "medium",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    
    # Check debt-to-income ratio
    monthly_income = profile.get('monthly_income', 0)
    current_loans = profile.get('current_loans', [])
    total_emi = sum([loan.get('emi', 0) for loan in current_loans])
    
    if monthly_income > 0:
        debt_to_income = (total_emi / monthly_income) * 100
        if debt_to_income > 40:
            alerts.append({
                "type": "error",
                "message": f"High debt-to-income ratio ({debt_to_income:.1f}%). Consider reducing debt.",
                "priority": "high",
                "timestamp": datetime.now().isoformat(),
                "seen": False
            })
        elif debt_to_income > 30:
            alerts.append({
                "type": "warning",
                "message": f"Debt-to-income ratio ({debt_to_income:.1f}%) is getting high. Monitor your finances.",
                "priority": "medium",
                "timestamp": datetime.now().isoformat(),
                "seen": False
            })
    
    # Check savings
    monthly_expense = profile.get('monthly_expense', 0)
    monthly_savings = monthly_income - monthly_expense - total_emi
    if monthly_savings < 0:
        alerts.append({
            "type": "error",
            "message": "You are spending more than your income. Review your expenses immediately.",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    elif monthly_savings < (monthly_income * 0.1):
        alerts.append({
            "type": "warning",
            "message": "Low monthly savings. Aim to save at least 10-20% of your income.",
            "priority": "medium",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    
    # EMI reminders (simulated - in real app, would check actual due dates)
    if current_loans:
        alerts.append({
            "type": "info",
            "message": f"You have {len(current_loans)} active loan(s). Ensure timely EMI payments.",
            "priority": "low",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    
    # Credit card reminders
    num_credit_cards = profile.get('num_credit_cards', 0)
    if num_credit_cards > 0:
        alerts.append({
            "type": "info",
            "message": f"Don't forget to pay your credit card bills on time. You have {num_credit_cards} card(s).",
            "priority": "low",
            "timestamp": datetime.now().isoformat(),
            "seen": False
        })
    
    # Save alerts
    existing_alerts = load_alerts()
    # Merge with existing alerts (avoid duplicates)
    alert_messages = {alert.get('message') for alert in existing_alerts}
    new_alerts = [alert for alert in alerts if alert.get('message') not in alert_messages]
    existing_alerts.extend(new_alerts)
    save_alerts(existing_alerts)
    
    return existing_alerts

def get_unseen_alerts_count():
    """Get count of unseen alerts"""
    alerts = load_alerts()
    unseen = [alert for alert in alerts if not alert.get('seen', False)]
    return len(unseen)

def mark_alert_as_seen(alert_index):
    """Mark an alert as seen"""
    alerts = load_alerts()
    if 0 <= alert_index < len(alerts):
        alerts[alert_index]['seen'] = True
        save_alerts(alerts)
        return True
    return False
