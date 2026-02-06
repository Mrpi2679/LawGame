from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Database setup for Vercel
DB_FILE = 'law_game.db'
if os.environ.get('VERCEL'):
    DB_FILE = f"/tmp/{DB_FILE}"

def get_db_connection():
    try:
        # Ensure database exists for Vercel
        if not os.path.exists(DB_FILE):
            from init_db import init_database
            init_database()
        
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    try:
        if not os.path.exists(DB_FILE):
            from init_db import init_database
            init_database()
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize database safely
init_db()

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled exception: {e}")
    flash('An error occurred. Please try again.')
    return redirect(url_for('login'))

@app.route('/')
def index():
    try:
        if 'user_id' in session:
            return redirect(url_for('mode_select'))
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Index route error: {e}")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not password:
                flash('Please enter both username and password')
                return render_template('login.html')
            
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
                    user_row = cursor.fetchone()
                    
                    if user_row and dict(user_row)['password'] == password:
                        user = dict(user_row)
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        return redirect(url_for('mode_select'))
                    else:
                        flash('Invalid username or password')
                except Exception as e:
                    print(f"Login query error: {e}")
                    flash('Database error occurred')
                finally:
                    conn.close()
            else:
                flash('Database connection failed')
        
        return render_template('login.html')
    except Exception as e:
        print(f"Login route error: {e}")
        flash('Login error occurred')
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not username or not password:
                flash('Please fill all fields')
                return render_template('signup.html')
            
            if password != confirm_password:
                flash('Passwords do not match')
                return render_template('signup.html')
            
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        flash('Username already exists')
                        return render_template('signup.html')
                    
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    user_id = cursor.lastrowid
                    session['user_id'] = user_id
                    session['username'] = username
                    return redirect(url_for('mode_select'))
                except Exception as e:
                    print(f"Signup query error: {e}")
                    flash('Registration failed')
                finally:
                    conn.close()
            else:
                flash('Database connection failed')
        
        return render_template('signup.html')
    except Exception as e:
        print(f"Signup route error: {e}")
        flash('Signup error occurred')
        return render_template('signup.html')

@app.route('/logout')
def logout():
    try:
        session.clear()
    except:
        pass
    return redirect(url_for('login'))

@app.route('/mode_select')
def mode_select():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('mode_select.html')
    except Exception as e:
        print(f"Mode select error: {e}")
        return redirect(url_for('login'))

@app.route('/levels')
def levels():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        conn = get_db_connection()
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, level_number, title, description FROM levels ORDER BY level_number")
                all_levels = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute("SELECT level_id FROM user_progress WHERE user_id = ? AND completed = 1", (user_id,))
                completed_levels = {dict(row)['level_id'] for row in cursor.fetchall()}
                
                levels_data = []
                for level in all_levels:
                    level_id = level['id']
                    level_num = level['level_number']
                    
                    if level_num == 1:
                        unlocked = True
                    else:
                        prev_level = next((l for l in all_levels if l['level_number'] == level_num - 1), None)
                        unlocked = prev_level['id'] in completed_levels if prev_level else False
                    
                    levels_data.append({
                        'id': level_id,
                        'level_number': level_num,
                        'title': level['title'],
                        'description': level['description'],
                        'unlocked': unlocked,
                        'completed': level_id in completed_levels
                    })
                
                return render_template('levels.html', levels=levels_data)
            except Exception as e:
                print(f"Levels query error: {e}")
                flash('Error loading levels')
            finally:
                conn.close()
        
        return redirect(url_for('mode_select'))
    except Exception as e:
        print(f"Levels route error: {e}")
        return redirect(url_for('mode_select'))

@app.route('/bot_mode')
def bot_mode():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        conn = get_db_connection()
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM bot_questions")
                total_questions = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM user_bot_progress WHERE user_id = ?", (user_id,))
                answered_questions = cursor.fetchone()[0]
                
                remaining_questions = total_questions - answered_questions
                
                return render_template('bot_question_selection.html', 
                                     total_questions=total_questions,
                                     answered_questions=answered_questions,
                                     remaining_questions=remaining_questions)
            except Exception as e:
                print(f"Bot mode query error: {e}")
                flash('Error loading bot mode')
            finally:
                conn.close()
        
        return redirect(url_for('mode_select'))
    except Exception as e:
        print(f"Bot mode route error: {e}")
        return redirect(url_for('mode_select'))

# Vercel serverless handler
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == '__main__':
    app.run(debug=False)