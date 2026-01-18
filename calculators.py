import math

def calculate_emi(principal, rate, tenure_months):
    """
    Calculate EMI using the formula: EMI = [P × R × (1+R)^N] / [(1+R)^N - 1]
    
    Args:
        principal: Loan amount
        rate: Annual interest rate (percentage)
        tenure_months: Loan tenure in months
    
    Returns:
        tuple: (EMI, Total Interest, Total Amount)
    """
    if rate == 0:
        emi = principal / tenure_months
        total_interest = 0
    else:
        # Convert annual rate to monthly rate
        monthly_rate = (rate / 100) / 12
        
        # Calculate EMI
        emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / \
              ((1 + monthly_rate) ** tenure_months - 1)
        
        # Calculate total interest
        total_interest = (emi * tenure_months) - principal
    
    total_amount = principal + total_interest
    
    return round(emi, 2), round(total_interest, 2), round(total_amount, 2)

def check_affordability(profile, new_emi):
    """
    Check if user can afford a new loan/product based on current financial situation
    
    Args:
        profile: User profile dictionary
        new_emi: EMI amount for new loan/product
    
    Returns:
        tuple: (is_affordable, available_income, affordability_percentage)
    """
    monthly_income = profile.get('monthly_income', 0)
    monthly_expense = profile.get('monthly_expense', 0)
    
    # Calculate current total EMIs
    current_loans = profile.get('current_loans', [])
    total_current_emi = sum([loan.get('emi', 0) for loan in current_loans])
    
    # Available income after expenses and current EMIs
    available_income = monthly_income - monthly_expense - total_current_emi
    
    # Check affordability (should have at least 20% buffer)
    is_affordable = available_income >= (new_emi * 1.2)
    
    # Calculate affordability percentage
    if available_income > 0:
        affordability_pct = (new_emi / available_income) * 100
    else:
        affordability_pct = 100
    
    return is_affordable, available_income, affordability_pct

def calculate_debt_to_income_ratio(profile):
    """
    Calculate debt-to-income ratio
    
    Args:
        profile: User profile dictionary
    
    Returns:
        float: Debt-to-income ratio as percentage
    """
    monthly_income = profile.get('monthly_income', 0)
    if monthly_income == 0:
        return 0
    
    # Total monthly debt payments (EMIs)
    current_loans = profile.get('current_loans', [])
    total_emi = sum([loan.get('emi', 0) for loan in current_loans])
    
    # Calculate ratio
    ratio = (total_emi / monthly_income) * 100
    return round(ratio, 2)

def calculate_credit_utilization_score(credit_utilization):
    """
    Calculate credit utilization score impact
    
    Args:
        credit_utilization: Credit utilization percentage
    
    Returns:
        str: Impact level (Good/Moderate/Poor)
    """
    if credit_utilization <= 30:
        return "Good"
    elif credit_utilization <= 60:
        return "Moderate"
    else:
        return "Poor"
