import mysql.connector # Changed from sqlite3
from mysql.connector import Error
import random
import smtplib
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Email Configuration ---
# It's better to use environment variables, but using your hardcoded values for now.
SENDER_EMAIL = "randomyt002@gmail.com"
SENDER_PASSWORD = "tuljliddhrqrebjx" # Note: There might be a trailing space in your original password.

# --- 🔌 Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'surakshapay',
    'user': 'root', # Assuming the user is 'root', which is common for local setups.
    'password': 'Ayush@123'
}

# --- Database Setup ---
def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def create_user_table():
    """Creates the user table in the MySQL database."""
    conn = get_db_connection()
    if conn is None:
        print("Could not connect to the database to create table.")
        return
        
    # Use a dictionary cursor to access rows by column name, similar to sqlite3.Row
    cursor = conn.cursor()
    # Updated SQL syntax for MySQL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            otp VARCHAR(10),
            is_verified BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# --- Helper Function: Send Email (No changes needed here) ---
def send_otp_email(receiver_email, otp):
    """Sends an email with the OTP code."""
    subject = "Your SurakshaPay Verification Code"
    body = f"Your OTP for SurakshaPay is: {otp}"
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# --- API Endpoints ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    # ... (rest of the data fetching is the same)
    full_name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')

    if not all([full_name, phone, email, password]):
        return jsonify({'message': 'All fields are required!'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed.'}), 500
        
    cursor = conn.cursor(dictionary=True) # Use a dictionary cursor

    cursor.execute('SELECT * FROM users WHERE email = %s', (email,)) # Use %s placeholder
    user = cursor.fetchone()

    if user and user['is_verified']:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Email already registered and verified.'}), 409

    otp = str(random.randint(100000, 999999))
    password_hash = generate_password_hash(password)

    if user and not user['is_verified']:
        cursor.execute(
            'UPDATE users SET full_name = %s, phone_number = %s, password_hash = %s, otp = %s WHERE email = %s', # Use %s
            (full_name, phone, password_hash, otp, email)
        )
    else:
        cursor.execute(
            'INSERT INTO users (full_name, phone_number, email, password_hash, otp) VALUES (%s, %s, %s, %s, %s)', # Use %s
            (full_name, phone, email, password_hash, otp)
        )
    
    conn.commit()
    cursor.close()
    conn.close()

    if send_otp_email(email, otp):
        return jsonify({'message': 'Signup successful! Please check your email for an OTP.'}), 200
    else:
        return jsonify({'message': 'Could not send OTP email. Please check server logs.'}), 500

@app.route('/verify', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({'message': 'Email and OTP are required!'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed.'}), 500
        
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM users WHERE email = %s', (email,)) # Use %s
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({'message': 'User not found.'}), 404

    if user['otp'] == otp:
        cursor.execute('UPDATE users SET is_verified = 1, otp = NULL WHERE email = %s', (email,)) # Use %s
        conn.commit()
        message, status_code = 'Account verified successfully! You can now log in.', 200
    else:
        message, status_code = 'Invalid OTP.', 400
    
    cursor.close()
    conn.close()
    return jsonify({'message': message}), status_code

# Add this new endpoint to your existing server.py file

@app.route('/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required!'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed.'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Case 1: User does not exist
    if not user:
        return jsonify({'message': 'Invalid email or password.'}), 401 # 401 Unauthorized

    # Case 2: User exists but has not verified their email via OTP
    if not user['is_verified']:
        return jsonify({'message': 'Account not verified. Please check your email for an OTP.'}), 403 # 403 Forbidden

    # Case 3: User exists, is verified, but password is incorrect
    if not check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Invalid email or password.'}), 401 # 401 Unauthorized

    # Case 4: Success!
    # In a real app, you would create a session token (JWT) here.
    # For now, we'll just send a success message.
    return jsonify({'message': 'Login successful!'}), 200
# Add these three new functions to your server.py file

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Handles the first step of password reset: sending an OTP."""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed.'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s AND is_verified = 1', (email,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        # Send a generic success message even if user doesn't exist
        # to prevent attackers from checking which emails are registered.
        return jsonify({'message': 'If an account with that email exists, an OTP has been sent.'}), 200

    # Generate and store a new OTP
    otp = str(random.randint(100000, 999999))
    cursor.execute('UPDATE users SET otp = %s WHERE email = %s', (otp, email))
    conn.commit()
    cursor.close()
    conn.close()

    # Send the email
    send_otp_email(email, otp) # This reuses your existing email function
    return jsonify({'message': 'If an account with that email exists, an OTP has been sent.'}), 200

@app.route('/verify-reset-otp', methods=['POST'])
def verify_reset_otp():
    """Verifies the OTP for a password reset."""
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({'message': 'Email and OTP are required.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed.'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT otp FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and user['otp'] == otp:
        return jsonify({'message': 'OTP verified successfully.'}), 200
    else:
        return jsonify({'message': 'Invalid OTP.'}), 400

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Sets the new password after successful OTP verification."""
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp') # We'll re-verify the OTP for security
    new_password = data.get('password')

    if not all([email, otp, new_password]):
        return jsonify({'message': 'All fields are required.'}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed.'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT otp FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()

    # Final security check: OTP must match
    if not user or user['otp'] != otp:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid OTP or session. Please try again.'}), 400

    # Hash the new password and update the database
    new_password_hash = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password_hash = %s, otp = NULL WHERE email = %s', (new_password_hash, email))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Password has been reset successfully. You can now log in.'}), 200

# --- Main Execution ---
if __name__ == '__main__':
    create_user_table()
    app.run(port=5000, debug=True)