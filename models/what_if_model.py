import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
import os

MODEL_DIR = "models"
WHATIF_MODEL_PATH = os.path.join(MODEL_DIR, "whatif_model.pkl")

def generate_training_data(n_samples=1500):
    """
    Generate synthetic training data for what-if predictions
    """
    np.random.seed(42)
    
    data = []
    for _ in range(n_samples):
        # Base financial state
        monthly_income = np.random.uniform(20000, 200000)
        monthly_expense = np.random.uniform(10000, monthly_income * 0.8)
        credit_score = np.random.uniform(400, 850)
        credit_utilization = np.random.uniform(0, 80)
        num_credit_cards = np.random.randint(0, 5)
        num_loans = np.random.randint(0, 4)
        total_emi = sum([np.random.uniform(2000, 20000) for _ in range(num_loans)])
        
        # Scenario changes
        scenario_type = np.random.choice(['new_loan', 'expense_increase', 'income_increase', 'pay_off_loan'])
        
        if scenario_type == 'new_loan':
            new_loan_amount = np.random.uniform(50000, 1000000)
            new_loan_rate = np.random.uniform(8, 18)
            new_loan_tenure = np.random.randint(1, 10)
            new_loan_emi = (new_loan_amount * (new_loan_rate/100/12) * (1 + new_loan_rate/100/12)**(new_loan_tenure*12)) / \
                          ((1 + new_loan_rate/100/12)**(new_loan_tenure*12) - 1)
            new_total_emi = total_emi + new_loan_emi
            new_monthly_expense = monthly_expense
            new_monthly_income = monthly_income
            new_credit_utilization = min(100, credit_utilization + np.random.uniform(5, 15))
        elif scenario_type == 'expense_increase':
            expense_increase = np.random.uniform(5000, 50000)
            new_total_emi = total_emi
            new_monthly_expense = monthly_expense + expense_increase
            new_monthly_income = monthly_income
            new_credit_utilization = min(100, credit_utilization + np.random.uniform(3, 10))
        elif scenario_type == 'income_increase':
            income_increase = np.random.uniform(10000, 100000)
            new_total_emi = total_emi
            new_monthly_expense = monthly_expense
            new_monthly_income = monthly_income + income_increase
            new_credit_utilization = max(0, credit_utilization - np.random.uniform(2, 8))
        else:  # pay_off_loan
            loan_to_pay = np.random.uniform(0, total_emi) if total_emi > 0 else 0
            new_total_emi = max(0, total_emi - loan_to_pay)
            new_monthly_expense = monthly_expense
            new_monthly_income = monthly_income
            new_credit_utilization = max(0, credit_utilization - np.random.uniform(5, 15))
        
        # Calculate derived features
        debt_to_income_before = (total_emi / monthly_income * 100) if monthly_income > 0 else 0
        debt_to_income_after = (new_total_emi / new_monthly_income * 100) if new_monthly_income > 0 else 0
        savings_rate_before = ((monthly_income - monthly_expense - total_emi) / monthly_income * 100) if monthly_income > 0 else 0
        savings_rate_after = ((new_monthly_income - new_monthly_expense - new_total_emi) / new_monthly_income * 100) if new_monthly_income > 0 else 0
        
        # Predict credit score change
        score_change = 0
        
        # Impact of debt changes
        if new_total_emi > total_emi:
            score_change -= (new_total_emi - total_emi) / 1000 * 10  # Negative impact
        elif new_total_emi < total_emi:
            score_change += (total_emi - new_total_emi) / 1000 * 15  # Positive impact
        
        # Impact of income changes
        if new_monthly_income > monthly_income:
            score_change += (new_monthly_income - monthly_income) / 10000 * 2  # Positive impact
        elif new_monthly_income < monthly_income:
            score_change -= (monthly_income - new_monthly_income) / 10000 * 3  # Negative impact
        
        # Impact of expense changes
        if new_monthly_expense > monthly_expense:
            score_change -= (new_monthly_expense - monthly_expense) / 10000 * 2  # Negative impact
        elif new_monthly_expense < monthly_expense:
            score_change += (monthly_expense - new_monthly_expense) / 10000 * 3  # Positive impact
        
        # Impact of credit utilization
        if new_credit_utilization > credit_utilization:
            score_change -= (new_credit_utilization - credit_utilization) * 0.5
        elif new_credit_utilization < credit_utilization:
            score_change += (credit_utilization - new_credit_utilization) * 0.8
        
        # Add some randomness
        score_change += np.random.uniform(-5, 5)
        
        predicted_score = max(300, min(900, credit_score + score_change))
        
        # Calculate predicted risk and eligibility
        if predicted_score >= 750 and debt_to_income_after < 30 and new_credit_utilization < 30:
            predicted_risk = "Low"
            predicted_eligibility = np.random.uniform(70, 100)
        elif predicted_score >= 650 and debt_to_income_after < 40 and new_credit_utilization < 50:
            predicted_risk = "Medium"
            predicted_eligibility = np.random.uniform(40, 75)
        else:
            predicted_risk = "High"
            predicted_eligibility = np.random.uniform(0, 45)
        
        data.append({
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'credit_score': credit_score,
            'credit_utilization': credit_utilization,
            'num_credit_cards': num_credit_cards,
            'total_emi': total_emi,
            'debt_to_income': debt_to_income_before,
            'savings_rate': savings_rate_before,
            'new_total_emi': new_total_emi,
            'new_monthly_income': new_monthly_income,
            'new_monthly_expense': new_monthly_expense,
            'new_credit_utilization': new_credit_utilization,
            'new_debt_to_income': debt_to_income_after,
            'new_savings_rate': savings_rate_after,
            'scenario_type': scenario_type,
            'predicted_score': predicted_score,
            'predicted_risk': predicted_risk,
            'predicted_eligibility': predicted_eligibility
        })
    
    return pd.DataFrame(data)

def train_model():
    """Train Random Forest model for what-if predictions"""
    print("Generating training data for what-if model...")
    df = generate_training_data(2000)
    
    # Features: current state + changes
    feature_cols = [
        'monthly_income', 'monthly_expense', 'credit_score', 'credit_utilization',
        'num_credit_cards', 'total_emi', 'debt_to_income', 'savings_rate',
        'new_total_emi', 'new_monthly_income', 'new_monthly_expense',
        'new_credit_utilization', 'new_debt_to_income', 'new_savings_rate'
    ]
    X = df[feature_cols]
    
    # Target: predicted credit score
    y_score = df['predicted_score']
    
    # Train model
    print("Training what-if model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=12)
    model.fit(X, y_score)
    
    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(WHATIF_MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print("What-if model trained and saved successfully!")
    return model

def load_whatif_model():
    """Load trained what-if model"""
    if os.path.exists(WHATIF_MODEL_PATH):
        with open(WHATIF_MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

def predict_what_if(profile, scenario):
    """
    Predict financial impact of a scenario
    
    Args:
        profile: Current user profile
        scenario: Scenario dictionary with type and parameters
    
    Returns:
        tuple: (predicted_credit_score, predicted_risk_category, predicted_eligibility)
    """
    # Load or train model
    model = load_whatif_model()
    if model is None:
        print("What-if model not found. Training new model...")
        model = train_model()
    
    # Extract current state
    monthly_income = profile.get('monthly_income', 0)
    monthly_expense = profile.get('monthly_expense', 0)
    credit_score = profile.get('credit_score', 650)
    credit_utilization = profile.get('credit_utilization', 0)
    num_credit_cards = profile.get('num_credit_cards', 0)
    current_loans = profile.get('current_loans', [])
    total_emi = sum([loan.get('emi', 0) for loan in current_loans])
    
    # Calculate current derived features
    debt_to_income = (total_emi / monthly_income * 100) if monthly_income > 0 else 0
    savings_rate = ((monthly_income - monthly_expense - total_emi) / monthly_income * 100) if monthly_income > 0 else 0
    
    # Apply scenario
    new_monthly_income = monthly_income
    new_monthly_expense = monthly_expense
    new_total_emi = total_emi
    new_credit_utilization = credit_utilization
    
    scenario_type = scenario.get('type', '')
    
    if scenario_type == 'Take a new loan':
        from utils.calculators import calculate_emi
        loan_amount = scenario.get('loan_amount', 0)
        rate = scenario.get('rate', 12)
        tenure = scenario.get('tenure', 3)
        new_loan_emi, _, _ = calculate_emi(loan_amount, rate, tenure * 12)
        new_total_emi = total_emi + new_loan_emi
        new_credit_utilization = min(100, credit_utilization + 10)
    
    elif scenario_type == 'Increase expenses':
        expense_increase = scenario.get('expense_increase', 0)
        new_monthly_expense = monthly_expense + expense_increase
        new_credit_utilization = min(100, credit_utilization + 5)
    
    elif scenario_type == 'Increase income':
        income_increase = scenario.get('income_increase', 0)
        new_monthly_income = monthly_income + income_increase
        new_credit_utilization = max(0, credit_utilization - 5)
    
    elif scenario_type == 'Pay off a loan':
        loan_index = scenario.get('loan_index', 0)
        if 0 <= loan_index < len(current_loans):
            loan_to_remove = current_loans[loan_index]
            new_total_emi = total_emi - loan_to_remove.get('emi', 0)
            new_credit_utilization = max(0, credit_utilization - 10)
    
    # Calculate new derived features
    new_debt_to_income = (new_total_emi / new_monthly_income * 100) if new_monthly_income > 0 else 0
    new_savings_rate = ((new_monthly_income - new_monthly_expense - new_total_emi) / new_monthly_income * 100) if new_monthly_income > 0 else 0
    
    # Prepare feature vector
    features = np.array([[
        monthly_income,
        monthly_expense,
        credit_score,
        credit_utilization,
        num_credit_cards,
        total_emi,
        debt_to_income,
        savings_rate,
        new_total_emi,
        new_monthly_income,
        new_monthly_expense,
        new_credit_utilization,
        new_debt_to_income,
        new_savings_rate
    ]])
    
    # Predict credit score
    predicted_score = model.predict(features)[0]
    predicted_score = max(300, min(900, predicted_score))
    
    # Determine risk category and eligibility
    if predicted_score >= 750 and new_debt_to_income < 30 and new_credit_utilization < 30:
        predicted_risk = "Low"
        predicted_eligibility = 75 + (predicted_score - 750) / 15
    elif predicted_score >= 650 and new_debt_to_income < 40 and new_credit_utilization < 50:
        predicted_risk = "Medium"
        predicted_eligibility = 40 + (predicted_score - 650) / 10
    else:
        predicted_risk = "High"
        predicted_eligibility = max(0, (predicted_score - 300) / 10)
    
    predicted_eligibility = max(0, min(100, predicted_eligibility))
    
    return round(predicted_score, 0), predicted_risk, round(predicted_eligibility, 2)
