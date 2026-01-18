import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Page configuration
st.set_page_config(
    page_title="Captain Credo - Credit Health Platform",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stApp {
        background-color: #0E1117;
    }
    .stSidebar {
        background-color: #1E1E1E;
    }
    h1, h2, h3 {
        color: #6C63FF;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .alert-badge {
        background-color: #FF4444;
        color: white;
        border-radius: 50%;
        padding: 0.2rem 0.5rem;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .stMetric {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #333;
    }
    .stDataFrame {
        background-color: #1E1E1E;
    }
    .stButton>button {
        background-color: #6C63FF;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #5A52E5;
    }
    .stSelectbox label, .stNumberInput label, .stTextInput label {
        color: #FAFAFA;
    }
    /* Style for top right buttons */
    div[data-testid="column"]:nth-of-type(2) button,
    div[data-testid="column"]:nth-of-type(3) button {
        width: 100%;
        font-size: 0.9rem;
        padding: 0.4rem 0.8rem;
    }
    /* Notification window scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #1E1E1E;
    }
    ::-webkit-scrollbar-thumb {
        background: #6C63FF;
        border-radius: 3px;
    }
    /* Logo styling */
    img[alt*="logo"] {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(108, 99, 255, 0.3);
        transition: transform 0.3s ease;
    }
    img[alt*="logo"]:hover {
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'alerts_count' not in st.session_state:
    st.session_state.alerts_count = 0
if 'show_notifications' not in st.session_state:
    st.session_state.show_notifications = False
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = None

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["🏠 Dashboard", "📊 Credit Health", "🧮 EMI Calculator", "💳 Loan Comparison", 
                 "🔮 What-If Simulator", "📈 Credit Score History"],
        icons=["house", "graph-up", "calculator", "bank", "magic", "chart-line"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#1E1E1E"},
            "icon": {"color": "#6C63FF", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "color": "#FAFAFA",
                "padding": "10px",
            },
            "nav-link-selected": {"background-color": "#6C63FF"},
        }
    )

# Import utility modules
try:
    from utils.data_handler import load_user_profile, save_user_profile, load_credit_history, save_credit_history, load_alerts, save_alerts
    from utils.calculators import calculate_emi, check_affordability
    from utils.alerts import generate_alerts, get_unseen_alerts_count
    from models.credit_health_model import predict_credit_health, load_credit_model
    from models.what_if_model import predict_what_if, load_whatif_model
    from utils.pdf_generator import generate_monthly_report
except ImportError as e:
    st.error(f"Module import error: {e}. Please ensure all utility files are created.")
    st.stop()

# Function to initialize mock credit history if needed
def initialize_mock_credit_history():
    """Initialize mock credit history if empty or has very few entries"""
    history = load_credit_history()
    if len(history) <= 1:
        mock_data = [
            {
                "date": "2025-07-15T10:00:00",
                "credit_score": 580,
                "notes": "Initial credit assessment"
            },
            {
                "date": "2025-08-15T10:00:00",
                "credit_score": 595,
                "notes": "Improved payment history"
            },
            {
                "date": "2025-09-15T10:00:00",
                "credit_score": 610,
                "notes": "Reduced credit utilization"
            },
            {
                "date": "2025-10-15T10:00:00",
                "credit_score": 625,
                "notes": "Consistent bill payments"
            },
            {
                "date": "2025-11-15T10:00:00",
                "credit_score": 640,
                "notes": "Paid off credit card debt"
            },
            {
                "date": "2025-12-15T10:00:00",
                "credit_score": 655,
                "notes": "Maintained good credit habits"
            },
            {
                "date": "2026-01-10T10:00:00",
                "credit_score": 650,
                "notes": "Took new loan - slight impact"
            }
        ]
        if history:
            existing_entry = history[0]
            mock_data.append(existing_entry)
        save_credit_history(mock_data)
        return True
    return False

# Load user profile for name display
if 'profile_for_header' not in st.session_state:
    profile_for_header = load_user_profile()
    st.session_state.profile_for_header = profile_for_header
else:
        profile_for_header = st.session_state.profile_for_header

if st.session_state.get('reload_profile', False):
    profile_for_header = load_user_profile()
    st.session_state.profile_for_header = profile_for_header

user_name = profile_for_header.get('name', '') if profile_for_header else ''
profile_button_text = user_name if user_name else "⚙️ Profile"
if len(profile_button_text) > 15:
    profile_button_text = profile_button_text[:12] + "..."

header_col1, header_col2, header_col3, header_col4 = st.columns([4, 5, 0.5, 0.5])
with header_col1:
    try:
        logo_path = r"C:\Users\Shoya\Desktop\Hackathon FInalized zip file\Hackathon\images\logo.png"
        st.image(logo_path, width=300)
    except Exception as e:
        st.write(f"Logo not found: {e}")

with header_col3:
    if st.button(profile_button_text, key="profile_btn", use_container_width=True):
        st.session_state.selected_page = "⚙️ Profile"
        st.session_state.show_notifications = False
        st.rerun()

with header_col4:
    alert_text = "🔔"
    if st.session_state.alerts_count > 0:
        alert_text = f"🔔 ({st.session_state.alerts_count})"
    if st.button(alert_text, key="alerts_btn", use_container_width=True):
        st.session_state.show_notifications = not st.session_state.show_notifications
        st.rerun()

# Notification dropdown window
if st.session_state.show_notifications:
    with st.container():
        st.markdown("---")
        st.markdown("### 🔔 Notifications")
        
        profile_for_alerts = load_user_profile()
        if profile_for_alerts:
            alerts = generate_alerts(profile_for_alerts)
            unseen_count = get_unseen_alerts_count()
            
            if unseen_count > 0:
                st.info(f"**{unseen_count} new notifications**")
            
            if alerts:
                alerts_sorted = sorted(alerts, key=lambda x: (
                    0 if x.get('type') == 'error' else 1 if x.get('type') == 'warning' else 2,
                    x.get('timestamp', '')
                ), reverse=True)
                
                for idx, alert in enumerate(alerts_sorted[:10]):
                    alert_type = alert.get('type', 'info')
                    is_seen = alert.get('seen', False)
                    message = alert.get('message', '')
                    timestamp = alert.get('timestamp', '')
                    
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            time_str = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            time_str = ""
                    else:
                        time_str = ""
                    
                    if not is_seen:
                        st.markdown("**🔴 NEW**")
                    
                    if alert_type == 'error':
                        st.error(f"{message} {f'({time_str})' if time_str else ''}")
                    elif alert_type == 'warning':
                        st.warning(f"{message} {f'({time_str})' if time_str else ''}")
                    else:
                        st.info(f"{message} {f'({time_str})' if time_str else ''}")
                    
                    st.markdown("---")
            else:
                st.success("✅ No active alerts. Your financial health looks good!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Mark All Read", key="mark_all_read", use_container_width=True):
                    all_alerts = load_alerts()
                    for alert in all_alerts:
                        alert['seen'] = True
                    save_alerts(all_alerts)
                    st.session_state.show_notifications = False
                    st.rerun()
            with col2:
                if st.button("View All Alerts", key="view_all_alerts", use_container_width=True):
                    st.session_state.selected_page = "🔔 Alerts"
                    st.session_state.show_notifications = False
                    st.rerun()
        else:
            st.warning("⚠️ Please set up your profile first to see alerts")
            if st.button("Close", key="close_notifications"):
                st.session_state.show_notifications = False
                st.rerun()

if st.session_state.selected_page:
    selected = st.session_state.selected_page
    st.session_state.selected_page = None

# Route to different pages
if selected == "🏠 Dashboard":
    st.title("Financial Dashboard")
    st.markdown("Welcome to your financial command center")
    
    profile = load_user_profile()
    if profile:
        st.session_state.user_profile = profile
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            credit_score = profile.get('credit_score', 0)
            st.metric("Credit Score", f"{credit_score}", delta=None)
        
        with col2:
            monthly_income = profile.get('monthly_income', 0)
            monthly_expense = profile.get('monthly_expense', 0)
            total_emi = sum([loan.get('emi', 0) for loan in profile.get('current_loans', [])])
            monthly_savings = monthly_income - monthly_expense - total_emi
            st.metric("Monthly Savings", f"₹{monthly_savings:,}", delta=None)
        
        with col3:
            st.metric("Total EMI", f"₹{total_emi:,}", delta=None)
        
        with col4:
            credit_utilization = profile.get('credit_utilization', 0)
            st.metric("Credit Utilization", f"{credit_utilization}%", delta=None)
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Income vs Expenses")
            income_expense_data = pd.DataFrame({
                'Category': ['Income', 'Expenses', 'EMI', 'Savings'],
                'Amount': [monthly_income, monthly_expense, total_emi, monthly_savings]
            })
            st.bar_chart(income_expense_data.set_index('Category'))
        
        with col2:
            st.subheader("Expense Breakdown")
            if monthly_expense > 0:
                expense_categories = {
                    'Food & Groceries': monthly_expense * 0.3,
                    'Transportation': monthly_expense * 0.2,
                    'Utilities': monthly_expense * 0.15,
                    'Entertainment': monthly_expense * 0.1,
                    'Shopping': monthly_expense * 0.15,
                    'Others': monthly_expense * 0.1
                }
                expense_df = pd.DataFrame({
                    'Category': list(expense_categories.keys()),
                    'Amount': list(expense_categories.values())
                })
                st.bar_chart(expense_df.set_index('Category'))
        
        st.markdown("---")
        
        # Credit Score Trend
        st.subheader("Credit Score Trend")
        history = load_credit_history()
        if history and len(history) > 0:
            df_history = pd.DataFrame(history)
            df_history['date'] = pd.to_datetime(df_history['date'], errors='coerce')
            df_history = df_history.sort_values('date')
            st.line_chart(df_history.set_index('date')['credit_score'])
        else:
            current_date = datetime.now().strftime('%Y-%m-%d')
            score_df = pd.DataFrame({
                'date': [current_date],
                'credit_score': [credit_score]
            })
            score_df['date'] = pd.to_datetime(score_df['date'], errors='coerce')
            st.line_chart(score_df.set_index('date')['credit_score'])
            st.info("Start tracking your credit score history by updating your profile regularly.")
        
        st.markdown("---")
        
        # Current Loans Summary
        st.subheader("Current Loans Summary")
        current_loans = profile.get('current_loans', [])
        if current_loans:
            loans_data = []
            for i, loan in enumerate(current_loans, 1):
                loans_data.append({
                    'Loan #': i,
                    'Amount': f"₹{loan.get('amount', 0):,}",
                    'Monthly EMI': f"₹{loan.get('emi', 0):,}",
                    'Remaining Tenure': f"{loan.get('remaining_tenure', 0)} months"
                })
            loans_df = pd.DataFrame(loans_data)
            st.dataframe(loans_df, use_container_width=True, hide_index=True)
        else:
            st.info("No active loans")
        
        # Credit Card Utilization
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credit Utilization")
            
            utilization = credit_utilization
            if utilization <= 30:
                st.success(f"✅ Good utilization: {utilization}%")
            elif utilization <= 60:
                st.warning(f"⚠️ Moderate utilization: {utilization}%")
            else:
                st.error(f"❌ High utilization: {utilization}%")
            
            util_data = pd.DataFrame({
                'Status': ['Used', 'Available'],
                'Percentage': [utilization, max(0, 100 - utilization)]
            })
            st.bar_chart(util_data.set_index('Status'))
        
        with col2:
            st.subheader("Financial Health Score")
            health_score = 0
            if credit_score >= 750:
                health_score += 30
            elif credit_score >= 650:
                health_score += 20
            elif credit_score >= 550:
                health_score += 10
            
            if credit_utilization <= 30:
                health_score += 25
            elif credit_utilization <= 60:
                health_score += 15
            else:
                health_score += 5
            
            if monthly_savings > 0:
                savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
                if savings_rate >= 20:
                    health_score += 25
                elif savings_rate >= 10:
                    health_score += 15
                else:
                    health_score += 10
            
            debt_to_income = (total_emi / monthly_income * 100) if monthly_income > 0 else 0
            if debt_to_income <= 30:
                health_score += 20
            elif debt_to_income <= 40:
                health_score += 10
            else:
                health_score += 5
            
            st.metric("Health Score", f"{health_score}/100")
            if health_score >= 75:
                st.success("Excellent financial health!")
            elif health_score >= 60:
                st.info("Good financial health")
            else:
                st.warning("Room for improvement")
    else:
        st.warning("⚠️ Please set up your profile first in the Profile section")

elif selected == "📊 Credit Health":
    st.title("Credit Health Analysis")
    st.markdown("AI-powered credit health assessment")
    
    profile = load_user_profile()
    if profile:
        try:
            eligibility, risk_category = predict_credit_health(profile)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Loan Eligibility Probability", f"{eligibility:.1f}%")
                if eligibility >= 70:
                    st.success("✅ High eligibility")
                elif eligibility >= 40:
                    st.warning("⚠️ Moderate eligibility")
                else:
                    st.error("❌ Low eligibility")
            
            with col2:
                st.metric("Risk Category", risk_category)
                if risk_category == "Low":
                    st.success("✅ Low risk profile")
                elif risk_category == "Medium":
                    st.warning("⚠️ Medium risk profile")
                else:
                    st.error("❌ High risk profile")
            
            st.markdown("---")
            st.subheader("Recommendations")
            if eligibility < 40:
                st.info("💡 Consider improving your credit score and reducing existing debt")
            elif risk_category == "High":
                st.info("💡 Focus on reducing credit utilization and paying bills on time")
            else:
                st.success("💡 Your credit health looks good! Maintain good financial habits.")
        except Exception as e:
            st.error(f"Error in credit health analysis: {e}")
    else:
        st.warning("⚠️ Please set up your profile first")

elif selected == "🧮 EMI Calculator":
    st.title("EMI Calculator & Tools")
    
    tab1, tab2 = st.tabs(["EMI Calculator", "Affordability Calculator"])
    
    with tab1:
        st.subheader("Calculate Your EMI")
        col1, col2 = st.columns(2)
        
        with col1:
            principal = st.number_input("Loan Amount (₹)", min_value=0, value=100000, step=10000)
            rate = st.number_input("Interest Rate (% per annum)", min_value=0.0, value=10.0, step=0.1)
        
        with col2:
            tenure_years = st.number_input("Loan Tenure (Years)", min_value=1, value=5, step=1)
            tenure_months = tenure_years * 12
        
        if st.button("Calculate EMI"):
            emi, total_interest, total_amount = calculate_emi(principal, rate, tenure_months)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Monthly EMI", f"₹{emi:,.2f}")
            with col2:
                st.metric("Total Interest", f"₹{total_interest:,.2f}")
            with col3:
                st.metric("Total Amount", f"₹{total_amount:,.2f}")
    
    with tab2:
        st.subheader("Check Affordability")
        profile = load_user_profile()
        
        if profile:
            new_loan_amount = st.number_input("New Loan Amount (₹)", min_value=0, value=50000, step=10000)
            new_rate = st.number_input("Interest Rate (% per annum)", min_value=0.0, value=12.0, step=0.1)
            new_tenure = st.number_input("Tenure (Years)", min_value=1, value=3, step=1)
            
            if st.button("Check Affordability"):
                emi, _, _ = calculate_emi(new_loan_amount, new_rate, new_tenure * 12)
                is_affordable, available_income, affordability_pct = check_affordability(profile, emi)
                
                monthly_income = profile.get('monthly_income', 0)
                salary_used_amount = emi
                salary_used_pct = (emi / monthly_income * 100) if monthly_income > 0 else 0
                
                st.metric("New Loan EMI", f"₹{emi:,.2f}")
                st.metric("Available Income", f"₹{available_income:,.2f}")
                st.metric("Amount of Salary Used", f"₹{salary_used_amount:,.2f} ({salary_used_pct:.1f}%)")
                
                if is_affordable:
                    st.success(f"✅ You can afford this loan! Uses {salary_used_pct:.1f}% of your monthly income.")
                else:
                    st.error(f"❌ This loan may not be affordable. It exceeds your available income.")
        else:
            st.warning("⚠️ Please set up your profile first")

elif selected == "💳 Loan Comparison":
    st.title("Loan Comparison")
    st.markdown("Compare loan options from different banks")
    
    try:
        with open('data/loan_options.json', 'r') as f:
            loans = json.load(f)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            loan_type_filter = st.selectbox("Loan Type", ["All"] + list(set([loan['type'] for loan in loans])))
        with col2:
            loan_amount = st.number_input("Loan Amount (₹)", min_value=0, value=500000, step=50000)
        with col3:
            tenure_years = st.number_input("Tenure (Years)", min_value=1, value=5, step=1)
        
        filtered_loans = loans
        if loan_type_filter != "All":
            filtered_loans = [loan for loan in loans if loan['type'] == loan_type_filter]
        
        comparison_data = []
        for loan in filtered_loans:
            emi, total_interest, total_amount = calculate_emi(loan_amount, loan['interest_rate'], tenure_years * 12)
            comparison_data.append({
                'Bank': loan['bank'],
                'Loan Type': loan['type'],
                'Interest Rate': f"{loan['interest_rate']}%",
                'EMI': f"₹{emi:,.2f}",
                'Total Interest': f"₹{total_interest:,.2f}",
                'Total Amount': f"₹{total_amount:,.2f}",
                'Processing Fee': loan.get('processing_fee', 'N/A')
            })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No loans match your criteria")
    except FileNotFoundError:
        st.error("Loan options file not found. Please ensure data/loan_options.json exists.")
    except Exception as e:
        st.error(f"Error loading loan data: {e}")

elif selected == "🔮 What-If Simulator":
    st.title("What-If Simulator")
    st.markdown("See how financial decisions affect your credit health")
    
    profile = load_user_profile()
    if profile:
        st.subheader("Current Status")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Credit Score", profile.get('credit_score', 0))
        with col2:
            st.metric("Monthly Income", f"₹{profile.get('monthly_income', 0):,}")
        with col3:
            st.metric("Monthly Expenses", f"₹{profile.get('monthly_expense', 0):,}")
        
        st.markdown("---")
        st.subheader("Simulate Scenario")
        
        scenario_type = st.selectbox("What would you like to simulate?", 
                                     ["Take a new loan", "Increase expenses", "Increase income", "Pay off a loan"])
        
        if scenario_type == "Take a new loan":
            new_loan_amt = st.number_input("New Loan Amount (₹)", min_value=0, value=100000)
            new_loan_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=12.0)
            new_loan_tenure = st.number_input("Tenure (Years)", min_value=1, value=3)
        
        elif scenario_type == "Increase expenses":
            expense_increase = st.number_input("Additional Monthly Expenses (₹)", min_value=0, value=5000)
        
        elif scenario_type == "Increase income":
            income_increase = st.number_input("Additional Monthly Income (₹)", min_value=0, value=10000)
        
        elif scenario_type == "Pay off a loan":
            if profile.get('current_loans'):
                loan_options = [f"Loan {i+1}: ₹{loan.get('amount', 0):,}" for i, loan in enumerate(profile.get('current_loans', []))]
                selected_loan_idx = st.selectbox("Select loan to pay off", range(len(loan_options)), format_func=lambda x: loan_options[x])
            else:
                st.info("No current loans to pay off")
                selected_loan_idx = None
        
        if st.button("Simulate Impact"):
            try:
                scenario = {"type": scenario_type}
                if scenario_type == "Take a new loan":
                    scenario.update({"loan_amount": new_loan_amt, "rate": new_loan_rate, "tenure": new_loan_tenure})
                elif scenario_type == "Increase expenses":
                    scenario.update({"expense_increase": expense_increase})
                elif scenario_type == "Increase income":
                    scenario.update({"income_increase": income_increase})
                elif scenario_type == "Pay off a loan" and selected_loan_idx is not None:
                    scenario.update({"loan_index": selected_loan_idx})
                
                predicted_score, predicted_risk, predicted_eligibility = predict_what_if(profile, scenario)
                
                st.markdown("---")
                st.subheader("Predicted Impact")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    score_change = predicted_score - profile.get('credit_score', 0)
                    st.metric("Predicted Credit Score", f"{predicted_score:.0f}", delta=f"{score_change:+.0f}")
                with col2:
                    st.metric("Predicted Risk Category", predicted_risk)
                with col3:
                    st.metric("Predicted Eligibility", f"{predicted_eligibility:.1f}%")
                
                comparison_df = pd.DataFrame({
                    'Metric': ['Credit Score', 'Risk Level', 'Eligibility %'],
                    'Before': [profile.get('credit_score', 0), 'Current', 0],
                    'After': [predicted_score, predicted_risk, predicted_eligibility]
                })
                st.bar_chart(comparison_df.set_index('Metric')[['Before', 'After']])
                
            except Exception as e:
                st.error(f"Error in simulation: {e}")
    else:
        st.warning("⚠️ Please set up your profile first")

elif selected == "📈 Credit Score History":
    st.title("Credit Score History")
    st.markdown("Analyze your credit score trends and past decisions with AI-powered insights")
    
    initialize_mock_credit_history()
    
    history = load_credit_history()
    profile = load_user_profile()
    
    if history and len(history) > 0:
        df_history = pd.DataFrame(history)
        df_history['date'] = pd.to_datetime(df_history['date'], errors='coerce')
        df_history = df_history.sort_values('date')
        
        st.subheader("Credit Score Trend Over Time")
        st.line_chart(df_history.set_index('date')['credit_score'])
        
        # Statistical Analysis
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Score", f"{df_history['credit_score'].iloc[-1]:.0f}")
        with col2:
            st.metric("Average Score", f"{df_history['credit_score'].mean():.0f}")
        with col3:
            st.metric("Highest Score", f"{df_history['credit_score'].max():.0f}")
        with col4:
            st.metric("Lowest Score", f"{df_history['credit_score'].min():.0f}")
        
        st.markdown("---")
        
        st.subheader("AI-Powered Pattern Analysis")
        
        if len(df_history) > 1:
            recent_trend = df_history['credit_score'].iloc[-1] - df_history['credit_score'].iloc[0]
            recent_change = df_history['credit_score'].iloc[-1] - df_history['credit_score'].iloc[-2] if len(df_history) > 1 else 0
            
            score_std = df_history['credit_score'].std()
            volatility_level = "Low" if score_std < 20 else "Medium" if score_std < 40 else "High"
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Overall Trend**")
                if recent_trend > 20:
                    st.success(f"✅ Excellent improvement: +{recent_trend:.0f} points")
                elif recent_trend > 0:
                    st.success(f"✅ Positive trend: +{recent_trend:.0f} points")
                elif recent_trend < -20:
                    st.error(f"❌ Significant decline: {recent_trend:.0f} points")
                elif recent_trend < 0:
                    st.warning(f"⚠️ Declining trend: {recent_trend:.0f} points")
                else:
                    st.info("📊 Stable performance")
            
            with col2:
                st.write("**Score Volatility**")
                st.metric("Volatility Level", volatility_level)
                if volatility_level == "Low":
                    st.success("✅ Consistent credit behavior")
                elif volatility_level == "Medium":
                    st.warning("⚠️ Some fluctuations detected")
                else:
                    st.error("❌ High volatility - review financial habits")
        
        st.markdown("---")
        st.subheader("Reality Check: What Could Have Been")
        
        if profile:
            current_score = profile.get('credit_score', 0)
            
            try:
                ideal_profile = profile.copy()
                ideal_profile['credit_utilization'] = min(30, ideal_profile.get('credit_utilization', 0))
                ideal_profile['credit_score'] = min(900, current_score + 50)
                
                ideal_eligibility, ideal_risk = predict_credit_health(ideal_profile)
                current_eligibility, current_risk = predict_credit_health(profile)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Current Situation**")
                    st.metric("Credit Score", f"{current_score}")
                    st.metric("Loan Eligibility", f"{current_eligibility:.1f}%")
                    st.metric("Risk Category", current_risk)
                
                with col2:
                    st.write("**If You Made Better Decisions**")
                    st.metric("Potential Score", f"{ideal_profile['credit_score']:.0f}", delta=f"+{ideal_profile['credit_score'] - current_score:.0f}")
                    st.metric("Potential Eligibility", f"{ideal_eligibility:.1f}%", delta=f"+{ideal_eligibility - current_eligibility:.1f}%")
                    st.metric("Potential Risk", ideal_risk)
                
                st.markdown("---")
                st.subheader("💡 Key Insights & Recommendations")
                
                insights = []
                if current_score < df_history['credit_score'].mean():
                    insights.append("• Your current score is below your historical average. Focus on consistent bill payments.")
                
                if profile.get('credit_utilization', 0) > 30:
                    insights.append(f"• Reducing credit utilization from {profile.get('credit_utilization', 0)}% to below 30% could improve your score significantly.")
                
                if ideal_eligibility > current_eligibility:
                    insights.append(f"• Making better financial decisions could increase your loan eligibility by {ideal_eligibility - current_eligibility:.1f}%.")
                
                if ideal_risk != current_risk and ideal_risk == "Low":
                    insights.append("• With better credit habits, you could achieve a Low risk profile.")
                
                if not insights:
                    insights.append("• You're on the right track! Maintain your good financial habits.")
                
                for insight in insights:
                    st.info(insight)
                
            except Exception as e:
                st.warning(f"Could not generate AI insights: {e}")
        
        st.markdown("---")
        st.subheader("Historical Decision Impact")
        
        if len(df_history) > 2:
            df_history['change'] = df_history['credit_score'].diff()
            positive_changes = df_history[df_history['change'] > 0]
            negative_changes = df_history[df_history['change'] < 0]
            
            col1, col2 = st.columns(2)
            with col1:
                if len(positive_changes) > 0:
                    avg_positive = positive_changes['change'].mean()
                    st.success(f"✅ Average improvement when making good decisions: +{avg_positive:.1f} points")
            with col2:
                if len(negative_changes) > 0:
                    avg_negative = negative_changes['change'].mean()
                    st.error(f"❌ Average decline from poor decisions: {avg_negative:.1f} points")
    else:
        st.info("No credit history available. Start using the platform to build your history!")
        
        if profile:
            st.markdown("---")
            st.subheader("Start Tracking Your Credit Journey")
            st.write("Update your profile regularly to see how your financial decisions impact your credit score over time.")
            current_score = profile.get('credit_score', 0)
            st.metric("Current Credit Score", f"{current_score}")

elif selected == "⚙️ Profile":
    st.session_state.show_notifications = False
    st.title("User Profile")
    st.markdown("Manage your financial information")
    
    if 'profile_loaded' not in st.session_state or st.session_state.get('reload_profile', False):
        profile = load_user_profile()
        st.session_state.user_profile = profile
        st.session_state.profile_loaded = True
        st.session_state.reload_profile = False
    else:
        profile = st.session_state.user_profile
    
    if profile is None:
        profile = {}
    
    with st.form("profile_form"):
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=profile.get('name', '') if profile else '', key="name_input")
        with col2:
            if profile and profile.get('birthdate'):
                try:
                    birthdate_value = datetime.strptime(profile.get('birthdate'), '%Y-%m-%d').date()
                except:
                    birthdate_value = datetime(2000, 1, 1).date()
            else:
                birthdate_value = datetime(2000, 1, 1).date()
            birthdate = st.date_input("Date of Birth", value=birthdate_value, key="birthdate_input")
        
        st.subheader("Financial Information")
        
        col1, col2 = st.columns(2)
        with col1:
            monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=profile.get('monthly_income', 0) if profile else 50000, step=1000)
            monthly_expense = st.number_input("Monthly Expenses (₹)", min_value=0, value=profile.get('monthly_expense', 0) if profile else 30000, step=1000)
            credit_score = st.number_input("Current Credit Score", min_value=300, max_value=900, value=profile.get('credit_score', 650) if profile else 650, step=1)
        
        with col2:
            credit_utilization = st.number_input("Credit Utilization (%)", min_value=0, max_value=100, value=profile.get('credit_utilization', 30) if profile else 30, step=1)
            num_credit_cards = st.number_input("Number of Credit Cards", min_value=0, value=profile.get('num_credit_cards', 1) if profile else 1, step=1)
        
        st.subheader("Current Loans")
        num_loans = st.number_input("Number of Current Loans", min_value=0, value=len(profile.get('current_loans', [])) if profile else 0, step=1)
        
        current_loans = []
        existing_loans = profile.get('current_loans', []) if profile else []
        
        for i in range(num_loans):
            existing_loan = existing_loans[i] if i < len(existing_loans) else {}
            
            with st.expander(f"Loan {i+1}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    loan_amount = st.number_input(f"Loan Amount (₹)", min_value=0, 
                                                  value=existing_loan.get('amount', 0), 
                                                  step=10000, key=f"loan_amt_{i}")
                with col2:
                    loan_emi = st.number_input(f"Monthly EMI (₹)", min_value=0, 
                                              value=existing_loan.get('emi', 0), 
                                              step=100, key=f"loan_emi_{i}")
                with col3:
                    loan_remaining = st.number_input(f"Remaining Tenure (Months)", min_value=0, 
                                                     value=existing_loan.get('remaining_tenure', 0), 
                                                     step=1, key=f"loan_tenure_{i}")
                current_loans.append({
                    "amount": int(loan_amount),
                    "emi": int(loan_emi),
                    "remaining_tenure": int(loan_remaining)
                })
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            old_score = profile.get('credit_score', 0) if profile else 0
            score_changed = (credit_score != old_score) if profile else True
            
            new_profile = {
                "name": name.strip() if name else "",
                "birthdate": birthdate.strftime('%Y-%m-%d') if birthdate else None,
                "monthly_income": int(monthly_income),
                "monthly_expense": int(monthly_expense),
                "credit_score": int(credit_score),
                "credit_utilization": int(credit_utilization),
                "num_credit_cards": int(num_credit_cards),
                "current_loans": current_loans,
                "last_updated": datetime.now().isoformat()
            }
            
            try:
                if save_user_profile(new_profile):
                    import time
                    time.sleep(0.2)
                    
                    saved_profile = load_user_profile()
                    if saved_profile:
                        st.session_state.user_profile = saved_profile
                        st.session_state.profile_loaded = True
                        st.session_state.profile_for_header = saved_profile
                        
                        if score_changed:
                            from utils.data_handler import add_credit_history_entry
                            add_credit_history_entry(credit_score, f"Profile updated - Score: {credit_score}")
                        
                        st.success("✅ Profile saved successfully!")
                        st.session_state.reload_profile = True
                        st.rerun()
                    else:
                        st.error("❌ Error: Profile was not saved correctly. Please try again.")
                else:
                    st.error("❌ Error saving profile. Please check file permissions and try again.")
            except Exception as e:
                st.error(f"❌ Error saving profile: {str(e)}")
                import traceback
                st.exception(e)
    
    current_profile_check = load_user_profile()
    if current_profile_check:
        st.markdown("---")
        with st.expander("📋 View Saved Profile Data (Verification)"):
            st.json(current_profile_check)
            st.caption("This shows the data currently saved in your profile file.")
    
    # PDF Export
    if current_profile_check:
        st.markdown("---")
        if st.button("📄 Generate Monthly Report PDF"):
            try:
                pdf_path = generate_monthly_report(current_profile_check)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_file,
                        file_name=f"monthly_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

elif selected == "🔔 Alerts":
    st.session_state.show_notifications = False
    st.title("Alerts & Notifications")
    
    profile = load_user_profile()
    if profile:
        alerts = generate_alerts(profile)
        
        if alerts:
            unseen_count = get_unseen_alerts_count()
            col1, col2 = st.columns([3, 1])
            with col1:
                st.metric("Unseen Alerts", unseen_count)
            with col2:
                if st.button("Mark All as Read"):
                    from utils.data_handler import load_alerts, save_alerts
                    all_alerts = load_alerts()
                    for alert in all_alerts:
                        alert['seen'] = True
                    save_alerts(all_alerts)
                    st.success("All alerts marked as read!")
                    st.rerun()
            
            st.markdown("---")
            
            alerts_sorted = sorted(alerts, key=lambda x: (
                0 if x.get('type') == 'error' else 1 if x.get('type') == 'warning' else 2,
                x.get('timestamp', '')
            ), reverse=True)
            
            for idx, alert in enumerate(alerts_sorted):
                alert_type = alert.get('type', 'info')
                is_seen = alert.get('seen', False)
                message = alert.get('message', '')
                timestamp = alert.get('timestamp', '')
                
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        time_str = timestamp
                else:
                    time_str = ""
                
                col1, col2 = st.columns([10, 1])
                with col1:
                    if alert_type == 'warning':
                        st.warning(f"⚠️ {message} {f'({time_str})' if time_str else ''}")
                    elif alert_type == 'error':
                        st.error(f"❌ {message} {f'({time_str})' if time_str else ''}")
                    else:
                        st.info(f"ℹ️ {message} {f'({time_str})' if time_str else ''}")
                
                with col2:
                    if not is_seen and st.button("✓", key=f"mark_seen_{idx}"):
                        from utils.alerts import mark_alert_as_seen
                        from utils.data_handler import load_alerts
                        all_alerts = load_alerts()
                        for i, a in enumerate(all_alerts):
                            if a.get('message') == message and a.get('timestamp') == timestamp:
                                mark_alert_as_seen(i)
                                break
                        st.rerun()
        else:
            st.success("✅ No active alerts. Your financial health looks good!")
    else:
        st.warning("⚠️ Please set up your profile first to see alerts")

# Update alerts count in session state
profile_for_alerts = load_user_profile()
if profile_for_alerts:
    generate_alerts(profile_for_alerts)
    st.session_state.alerts_count = get_unseen_alerts_count()
else:
    st.session_state.alerts_count = 0
