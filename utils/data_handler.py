import json
import os
from datetime import datetime

DATA_DIR = "data"

def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_user_profile():
    """Load user profile from JSON file"""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "user_profile.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user profile: {e}")
            import traceback
            traceback.print_exc()
            return None
    return None

def save_user_profile(profile):
    """Save user profile to JSON file"""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "user_profile.json")
    
    try:
        # Create a temporary file first, then rename (atomic write)
        temp_file = file_path + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
            f.flush()  # Ensure data is written to disk
            os.fsync(f.fileno())  # Force write to disk
        
        # Atomic rename (works on Windows and Unix)
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_file, file_path)
        
        # Verify the file was written correctly
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)  # Verify it's valid JSON
        
        return True
    except Exception as e:
        print(f"Error saving user profile: {e}")
        import traceback
        traceback.print_exc()
        # Clean up temp file if it exists
        temp_file = file_path + ".tmp"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False

def load_credit_history():
    """Load credit history from JSON file"""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "credit_history.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading credit history: {e}")
            return []
    return []

def save_credit_history(history):
    """Save credit history to JSON file"""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "credit_history.json")
    
    try:
        with open(file_path, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving credit history: {e}")
        return False

def add_credit_history_entry(credit_score, notes=""):
    """Add a new entry to credit history"""
    history = load_credit_history()
    new_entry = {
        "date": datetime.now().isoformat(),
        "credit_score": credit_score,
        "notes": notes
    }
    history.append(new_entry)
    save_credit_history(history)
    return True

def load_alerts():
    """Load alerts from JSON file"""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "alerts.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading alerts: {e}")
            return []
    return []

def save_alerts(alerts):
    """Save alerts to JSON file"""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "alerts.json")
    
    try:
        with open(file_path, 'w') as f:
            json.dump(alerts, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving alerts: {e}")
        return False
