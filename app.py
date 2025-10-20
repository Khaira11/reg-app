from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2 import Error
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# PostgreSQL configuration
db_config = {
    'host': os.getenv('DB_HOST', '192.168.117.188'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'database': os.getenv('DB_NAME', 'registration_db'),
    'port': os.getenv('DB_PORT', '5432')
}

def create_connection():
    """Create database connection"""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            connection = psycopg2.connect(**db_config)
            return connection
        except Error as e:
            print(f"Attempt {attempt + 1} failed: Error connecting to PostgreSQL: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to database.")
                return None

def init_db():
    """Initialize database and table"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            connection.commit()
            cursor.close()
            connection.close()
            print("Database table initialized successfully!")
            
        except Error as e:
            print(f"Error initializing database: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    
    if not username or not email:
        flash('Please fill in all fields!', 'error')
        return redirect(url_for('index'))
    
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Username or email already exists!', 'error')
                return redirect(url_for('index'))
            
            # Insert new user
            cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
            connection.commit()
            
            flash('Registration successful!', 'success')
            
        except Error as e:
            flash(f'Error: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    else:
        flash('Could not connect to database!', 'error')
    
    return redirect(url_for('index'))

@app.route('/users')
def view_users():
    connection = create_connection()
    users = []
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC")
            users_data = cursor.fetchall()
            
            # Convert to list of dictionaries for easier template handling
            users = []
            for user in users_data:
                users.append({
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'created_at': user[3]
                })
                
        except Error as e:
            flash(f'Error fetching users: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    else:
        flash('Could not connect to database!', 'error')
    
    return render_template('users.html', users=users)

if __name__ == '__main__':
    # Initialize database when app starts
    print("Initializing database...")
    init_db()
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
