from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'simple-deployment-key'

DB_FILE = '/tmp/law_game.db' if os.environ.get('VERCEL') else 'law_game.db'

def init_db():
    if not os.path.exists(DB_FILE):
        from init_db import init_database
        init_database()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            return redirect(url_for('mode_select'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/mode_select')
def mode_select():
    return render_template('mode_select.html')

# Vercel handler
def handler(environ, start_response):
    init_db()
    return app(environ, start_response)

if __name__ == '__main__':
    init_db()
    app.run(debug=False)