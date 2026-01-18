import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import pickle
import os

MODEL_DIR = "models"
CREDIT_MODEL_PATH = os.path.join(MODEL_DIR, "credit_health_model.pkl")
ELIGIBILITY_MODEL_PATH = os.path.join(MODEL_DIR, "eligibility_model.pkl")

def generate_training_data(n_samples=1000):
    """
    Generate synthetic training data for credit health analysis
    """
    np.random.seed(42)
    
    data = []
    for _ in range(n_samples):
        monthly_income = np.random.uniform(20000, 200000)
        monthly_expense = np.random.uniform(10000, monthly_income * 0.8)
        credit_score = np.random.uniform(300, 900)
        credit_utilization = np.random.uniform(0, 100)
        num_credit_cards = np.random.randint(0, 5)
        
        # Calculate total EMI (simulate 0-3 loans)
        num_loans = np.random.randint(0, 4)
        total_emi = 0
        for _ in range(num_loans):
            loan_emi = np.random.uniform(2000, 20000)
            total_emi += loan_emi
        
        # Calculate features
        debt_to_income = (total_emi / monthly_income * 100) if monthly_income > 0 else 0
        savings_rate = ((monthly_income - monthly_expense - total_emi) / monthly_income * 100) if monthly_income > 0 else 0
        
        # Determine risk category (Low/Medium/High)
        risk_score = 0
        if credit_score < 600:
            risk_score += 3
        elif credit_score < 700:
            risk_score += 2
        else:
            risk_score += 1
        
        if credit_utilization > 60:
            risk_score += 2
        elif credit_utilization > 30:
            risk_score += 1
        
        if debt_to_income > 40:
            risk_score += 2
        elif debt_to_income > 30:
            risk_score += 1
        
        if savings_rate < 0:
            risk_score += 2
        elif savings_rate < 10:
            risk_score += 1
        
        if risk_score <= 3:
            risk_category = "Low"
        elif risk_score <= 5:
            risk_category = "Medium"
        else:
            risk_category = "High"
        
        # Calculate eligibility probability (0-100%)
        base_eligibility = min(credit_score / 9, 100)  # Scale credit score to 0-100
        if credit_utilization > 60:
            base_eligibility *= 0.7
        elif credit_utilization > 30:
            base_eligibility *= 0.85
        
        if debt_to_income > 40:
            base_eligibility *= 0.6
        elif debt_to_income > 30:
            base_eligibility *= 0.8
        
        if savings_rate < 0:
            base_eligibility *= 0.5
        elif savings_rate < 10:
            base_eligibility *= 0.9
        
        eligibility_probability = max(0, min(100, base_eligibility + np.random.uniform(-5, 5)))
        
        data.append({
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'credit_score': credit_score,
            'credit_utilization': credit_utilization,
            'num_credit_cards': num_credit_cards,
            'total_emi': total_emi,
            'debt_to_income': debt_to_income,
            'savings_rate': savings_rate,
            'risk_category': risk_category,
            'eligibility_probability': eligibility_probability
        })
    
    return pd.DataFrame(data)

def train_models():
    """Train Random Forest models for credit health analysis"""
    print("Generating training data...")
    df = generate_training_data(2000)
    
    # Features
    feature_cols = ['monthly_income', 'monthly_expense', 'credit_score', 'credit_utilization', 
                    'num_credit_cards', 'total_emi', 'debt_to_income', 'savings_rate']
    X = df[feature_cols]
    
    # Targets
    y_risk = df['risk_category']
    y_eligibility = df['eligibility_probability']
    
    # Train risk category classifier
    print("Training risk category model...")
    risk_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    risk_model.fit(X, y_risk)
    
    # Train eligibility probability regressor
    print("Training eligibility probability model...")
    eligibility_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    eligibility_model.fit(X, y_eligibility)
    
    # Save models
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(CREDIT_MODEL_PATH, 'wb') as f:
        pickle.dump(risk_model, f)
    
    with open(ELIGIBILITY_MODEL_PATH, 'wb') as f:
        pickle.dump(eligibility_model, f)
    
    print("Models trained and saved successfully!")
    return risk_model, eligibility_model

def load_credit_model():
    """Load trained credit health models"""
    risk_model = None
    eligibility_model = None
    
    if os.path.exists(CREDIT_MODEL_PATH):
        with open(CREDIT_MODEL_PATH, 'rb') as f:
            risk_model = pickle.load(f)
    
    if os.path.exists(ELIGIBILITY_MODEL_PATH):
        with open(ELIGIBILITY_MODEL_PATH, 'rb') as f:
            eligibility_model = pickle.load(f)
    
    return risk_model, eligibility_model

def predict_credit_health(profile):
    """
    Predict credit health (eligibility probability and risk category)
    
    Args:
        profile: User profile dictionary
    
    Returns:
        tuple: (eligibility_probability, risk_category)
    """
    # Load or train models
    risk_model, eligibility_model = load_credit_model()
    
    if risk_model is None or eligibility_model is None:
        print("Models not found. Training new models...")
        risk_model, eligibility_model = train_models()
    
    # Extract features from profile
    monthly_income = profile.get('monthly_income', 0)
    monthly_expense = profile.get('monthly_expense', 0)
    credit_score = profile.get('credit_score', 650)
    credit_utilization = profile.get('credit_utilization', 0)
    num_credit_cards = profile.get('num_credit_cards', 0)
    
    # Calculate total EMI
    current_loans = profile.get('current_loans', [])
    total_emi = sum([loan.get('emi', 0) for loan in current_loans])
    
    # Calculate derived features
    debt_to_income = (total_emi / monthly_income * 100) if monthly_income > 0 else 0
    savings_rate = ((monthly_income - monthly_expense - total_emi) / monthly_income * 100) if monthly_income > 0 else 0
    
    # Prepare feature vector
    features = np.array([[
        monthly_income,
        monthly_expense,
        credit_score,
        credit_utilization,
        num_credit_cards,
        total_emi,
        debt_to_income,
        savings_rate
    ]])
    
    # Make predictions
    risk_category = risk_model.predict(features)[0]
    eligibility_probability = eligibility_model.predict(features)[0]
    
    # Ensure eligibility is in valid range
    eligibility_probability = max(0, min(100, eligibility_probability))
    
    return round(eligibility_probability, 2), risk_category
