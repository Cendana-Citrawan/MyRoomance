import hashlib
import re
from .connection import get_connection

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    conn = get_connection()
    if not conn:
        return "Error", "Database connection failed.", None, None
    
    if not email or not password:
        return "Failed", "Email and password cannot be empty.", None, None
    else:
        try:
            cursor = conn.cursor(dictionary=True, prepared=True)
            hashed_password = hash_password(password)
            cursor.execute(
                "SELECT UserID, Role FROM User WHERE Email = %s AND Password = %s",
                (email, hashed_password)
            )
            
            user = cursor.fetchone()
            
            return ("Success", "Login successful.", user['UserID'], user['Role']) if user else ("Failed", "Invalid email or password.", None, None)

        except:
            return "Error", "Try again login error.", None, None
        finally:
            cursor.close()

def register_user(email, password, confirm_password, role="Student"):
    conn = get_connection()
    
    if not conn:
        return "Error", "Database connection failed."
    
    if not email or not password or not confirm_password:
        return "Failed", "Email, password, and confirm password cannot be empty."
    elif not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!])(?=\S+$).{8,}$", password):
        return "Failed", "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, one special character (e.g., @, #, $, %, ^, &, +, =, !), and no whitespace."
    elif password != confirm_password:
        return "Failed", "Passwords do not match."
    else:
        try:
            cursor = conn.cursor()
            hashed_password = hash_password(password)
        
            cursor.execute("SELECT Email FROM User WHERE Email = %s", (email,))
            if cursor.fetchone():
                return "Failed", "Email already registered"
            
            cursor.execute(
                "INSERT INTO User (Email, Password, Role) VALUES (%s, %s, %s)",
                (email, hashed_password, role)
            )
            
            cursor.execute(
                "INSERT INTO Profile (UserID) VALUES (%s)",
                (cursor.lastrowid,)
            )
            
            conn.commit()
            return "Success", "Registration successful."
        except:
            conn.rollback()
            return "Error", f"Try again registration error."
        finally:
            cursor.close()