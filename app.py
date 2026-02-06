from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'simple-deployment-key'

DB_FILE = '/tmp/law_game.db' if os.environ.get('VERCEL') else 'law_game.db'

def init_db():
    try:
        if not os.path.exists(DB_FILE):
            from init_db import init_database
            init_database()
    except:
        pass

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username and password:
            session['user_id'] = 1
            session['username'] = username
            return redirect(url_for('mode_select'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/mode_select')
def mode_select():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('mode_select.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Vercel expects this exact signature
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)