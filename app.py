from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import random
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Database file path - works in both local and Vercel environments
DB_FILE = os.environ.get('DATABASE_URL', 'law_game.db') or 'law_game.db'

def get_db_connection():
    try:
        # For Vercel serverless, use /tmp directory for database
        db_path = DB_FILE
        if os.environ.get('VERCEL'):
            db_path = f"/tmp/{os.path.basename(DB_FILE)}"
            # Copy database to /tmp if it exists in project root
            if not os.path.exists(db_path) and os.path.exists(DB_FILE):
                import shutil
                shutil.copy2(DB_FILE, db_path)
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    db_path = DB_FILE
    if os.environ.get('VERCEL'):
        db_path = f"/tmp/{os.path.basename(DB_FILE)}"
    
    if not os.path.exists(db_path):
        try:
            from init_db import init_database
            init_database()
        except Exception as e:
            print(f"Error initializing database: {e}")

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('mode_select'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password FROM users WHERE username = ?",
                    (username,)
                )
                user_row = cursor.fetchone()
                
                if user_row:
                    user = dict(user_row)
                    if user['password'] == password:
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        cursor.close()
                        conn.close()
                        return redirect(url_for('mode_select'))
                    else:
                        flash('Invalid username or password')
                else:
                    flash('Invalid username or password')
            except sqlite3.Error as e:
                flash('Database error occurred')
                print(f"Error: {e}")
            finally:
                if conn:
                    conn.close()
        else:
            flash('Database connection failed')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
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
                cursor.execute(
                    "SELECT id FROM users WHERE username = ?",
                    (username,)
                )
                if cursor.fetchone():
                    flash('Username already exists')
                    cursor.close()
                    conn.close()
                    return render_template('signup.html')
                
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
                user_id = cursor.lastrowid
                cursor.close()
                conn.close()
                
                session['user_id'] = user_id
                session['username'] = username
                return redirect(url_for('mode_select'))
            except sqlite3.Error as e:
                flash('Registration failed')
                print(f"Error: {e}")
            finally:
                if conn:
                    conn.close()
        else:
            flash('Database connection failed')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reset_bot_questions')
def reset_bot_questions():
    """Reset user's bot progress (clear answered questions from database)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Clear any active bot session
    if 'bot_session' in session:
        session.pop('bot_session')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_bot_progress WHERE user_id = ?", (user_id,))
            conn.commit()
            cursor.close()
            flash('Your bot progress has been reset. All questions are now available.')
        except sqlite3.Error as e:
            flash('Error resetting progress')
            print(f"Error: {e}")
        finally:
            conn.close()
    
    return redirect(url_for('bot_mode'))

@app.route('/mode_select')
def mode_select():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('mode_select.html')

@app.route('/levels')
def levels():
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
            
            cursor.close()
            conn.close()
            
            return render_template('levels.html', levels=levels_data)
        except sqlite3.Error as e:
            flash('Error loading levels')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return redirect(url_for('mode_select'))

@app.route('/play_level/<int:level_id>')
def play_level(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, level_number, title FROM levels WHERE id = ?", (level_id,))
            level_row = cursor.fetchone()
            
            if not level_row:
                flash('Level not found')
                cursor.close()
                conn.close()
                return redirect(url_for('levels'))
            
            level = dict(level_row)
            level_num = level['level_number']
            
            if level_num == 1:
                unlocked = True
            else:
                cursor.execute("SELECT id FROM levels WHERE level_number = ?", (level_num - 1,))
                prev_level_row = cursor.fetchone()
                if prev_level_row:
                    prev_level = dict(prev_level_row)
                    cursor.execute("SELECT completed FROM user_progress WHERE user_id = ? AND level_id = ?", (user_id, prev_level['id']))
                    prev_progress_row = cursor.fetchone()
                    unlocked = prev_progress_row and prev_progress_row['completed'] == 1
                else:
                    unlocked = False
            
            if not unlocked:
                flash('This level is locked. Complete the previous level first.')
                cursor.close()
                conn.close()
                return redirect(url_for('levels'))
            
            cursor.execute("SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation FROM questions WHERE level_id = ? ORDER BY id", (level_id,))
            questions = [dict(row) for row in cursor.fetchall()]
            
            if not questions:
                flash('No questions available for this level')
                cursor.close()
                conn.close()
                return redirect(url_for('levels'))
            
            cursor.close()
            conn.close()
            
            return render_template('play_level.html', level=level, questions=questions)
        except sqlite3.Error as e:
            flash('Error loading level')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return redirect(url_for('levels'))

@app.route('/submit_level/<int:level_id>', methods=['POST'])
def submit_level(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, correct_answer FROM questions WHERE level_id = ?", (level_id,))
            questions = [dict(row) for row in cursor.fetchall()]
            
            user_answers = {q['id']: request.form.get(f'question_{q["id"]}') for q in questions}
            
            correct_count = 0
            total_questions = len(questions)
            results = []
            
            for question in questions:
                q_id = question['id']
                correct = question['correct_answer']
                user_answer = user_answers.get(q_id)
                is_correct = (user_answer == correct)
                
                if is_correct:
                    correct_count += 1
                
                cursor.execute("SELECT question_text, option_a, option_b, option_c, option_d, explanation FROM questions WHERE id = ?", (q_id,))
                q_details = dict(cursor.fetchone())
                
                results.append({
                    'question_id': q_id,
                    'question_text': q_details['question_text'],
                    'user_answer': user_answer,
                    'correct_answer': correct,
                    'is_correct': is_correct,
                    'explanation': q_details['explanation'],
                    'options': {'A': q_details['option_a'], 'B': q_details['option_b'], 'C': q_details['option_c'], 'D': q_details['option_d']}
                })
            
            completed = (correct_count == total_questions)
            cursor.execute("SELECT id FROM user_progress WHERE user_id = ? AND level_id = ?", (user_id, level_id))
            
            if cursor.fetchone():
                cursor.execute("UPDATE user_progress SET score = ?, completed = ? WHERE user_id = ? AND level_id = ?", (correct_count, 1 if completed else 0, user_id, level_id))
            else:
                cursor.execute("INSERT INTO user_progress (user_id, level_id, score, completed) VALUES (?, ?, ?, ?)", (user_id, level_id, correct_count, 1 if completed else 0))
            
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return render_template('play_level.html', 
                                 level={'id': level_id, 'title': 'Results'},
                                 questions=[],
                                 results=results,
                                 score=correct_count,
                                 total=total_questions,
                                 completed=completed)
        except sqlite3.Error as e:
            flash('Error submitting level')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return redirect(url_for('levels'))

@app.route('/bot_mode')
def bot_mode():
    """Show question selection interface for bot mode"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get total questions
            cursor.execute("SELECT COUNT(*) FROM bot_questions")
            total_questions = cursor.fetchone()[0]
            
            # Get user's answered questions
            cursor.execute("SELECT COUNT(*) FROM user_bot_progress WHERE user_id = ?", (user_id,))
            answered_questions = cursor.fetchone()[0]
            
            remaining_questions = total_questions - answered_questions
            
            cursor.close()
            conn.close()
            
            return render_template('bot_question_selection.html', 
                                 total_questions=total_questions,
                                 answered_questions=answered_questions,
                                 remaining_questions=remaining_questions)
        except sqlite3.Error as e:
            flash('Error loading bot mode')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return redirect(url_for('mode_select'))

@app.route('/start_bot_session', methods=['POST'])
def start_bot_session():
    """Start a new bot session with selected number of questions"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    question_count = int(request.form.get('question_count', 5))
    shuffle_questions = request.form.get('shuffle', 'off') == 'on'
    
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get questions the user hasn't answered yet
            cursor.execute("""
                SELECT bq.id, bq.question_text, bq.option_a, bq.option_b, bq.option_c, bq.option_d, bq.correct_answer, bq.explanation
                FROM bot_questions bq
                LEFT JOIN user_bot_progress ubp ON bq.id = ubp.question_id AND ubp.user_id = ?
                WHERE ubp.question_id IS NULL
            """, (user_id,))
            
            available_questions = [dict(row) for row in cursor.fetchall()]
            
            if shuffle_questions:
                random.shuffle(available_questions)
            
            # Select the requested number of questions
            session_questions = available_questions[:question_count]
            
            if session_questions:
                # Initialize session data
                session['bot_session'] = {
                    'questions': session_questions,
                    'current_index': 0,
                    'user_score': 0,
                    'ai_score': 0,
                    'user_answers': [],
                    'ai_answers': []
                }
                
                # Get the first question
                current_question = session_questions[0]
                
                cursor.close()
                conn.close()
                
                return render_template('bot_mode.html', 
                                     question=current_question, 
                                     show_result=False,
                                     session_data=session['bot_session'],
                                     question_number=1,
                                     total_questions=len(session_questions))
            else:
                flash('No new questions available')
        except sqlite3.Error as e:
            flash('Error starting bot session')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return redirect(url_for('bot_mode'))

@app.route('/submit_bot_answer', methods=['POST'])
def submit_bot_answer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_answer = request.form.get('answer')
    
    if 'bot_session' not in session:
        return redirect(url_for('bot_mode'))
    
    bot_session = session['bot_session']
    current_index = bot_session['current_index']
    current_question = bot_session['questions'][current_index]
    
    # Check if user answer is correct
    is_user_correct = (user_answer == current_question['correct_answer'])
    
    # Generate AI answer (simulate with 70% accuracy for challenge)
    ai_accuracy = 0.7
    if random.random() < ai_accuracy:
        ai_answer = current_question['correct_answer']
        is_ai_correct = True
    else:
        # AI picks wrong answer
        wrong_answers = ['A', 'B', 'C', 'D']
        wrong_answers.remove(current_question['correct_answer'])
        ai_answer = random.choice(wrong_answers)
        is_ai_correct = False
    
    # Update scores
    if is_user_correct:
        bot_session['user_score'] += 1
    if is_ai_correct:
        bot_session['ai_score'] += 1
    
    # Store answers
    bot_session['user_answers'].append({
        'question_id': current_question['id'],
        'answer': user_answer,
        'is_correct': is_user_correct
    })
    
    bot_session['ai_answers'].append({
        'question_id': current_question['id'],
        'answer': ai_answer,
        'is_correct': is_ai_correct
    })
    
    # Save user progress to database
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_bot_progress (user_id, question_id, is_correct)
                VALUES (?, ?, ?)
            """, (user_id, current_question['id'], 1 if is_user_correct else 0))
            conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print(f"Error saving progress: {e}")
        finally:
            conn.close()
    
    # Check if session is complete
    current_index += 1
    if current_index >= len(bot_session['questions']):
        # Session complete - show results
        return render_template('bot_results.html',
                             user_score=bot_session['user_score'],
                             ai_score=bot_session['ai_score'],
                             total_questions=len(bot_session['questions']),
                             user_answers=bot_session['user_answers'],
                             ai_answers=bot_session['ai_answers'],
                             questions=bot_session['questions'])
    
    # Move to next question
    bot_session['current_index'] = current_index
    session['bot_session'] = bot_session
    
    next_question = bot_session['questions'][current_index]
    
    return render_template('bot_mode.html',
                         question=next_question,
                         show_result=True,
                         previous_question=current_question,
                         user_answer=user_answer,
                         ai_answer=ai_answer,
                         is_user_correct=is_user_correct,
                         is_ai_correct=is_ai_correct,
                         session_data=bot_session,
                         question_number=current_index + 1,
                         total_questions=len(bot_session['questions']))

@app.route('/scenario_chains')
def scenario_chains():
    """Display available scenario chains"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    scenarios = []
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, domain, law_involved, title FROM scenario_chains ORDER BY id")
            scenarios = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            flash('Error loading scenarios')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return render_template('scenario_chains.html', scenarios=scenarios)

@app.route('/play_scenario/<int:scenario_id>')
def play_scenario(scenario_id):
    """Start or continue a scenario chain"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get current step from session
    current_step = session.get(f'scenario_{scenario_id}_step', 1)
    user_answers = session.get(f'scenario_{scenario_id}_answers', {})
    
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get scenario info
            cursor.execute("SELECT id, domain, law_involved, title FROM scenario_chains WHERE id = ?", (scenario_id,))
            scenario = dict(cursor.fetchone())
            
            # Get current step
            cursor.execute("SELECT * FROM scenario_steps WHERE scenario_id = ? AND step_number = ?", (scenario_id, current_step))
            step_row = cursor.fetchone()
            
            if step_row:
                step = dict(step_row)
                return render_template('play_scenario.html', scenario=scenario, step=step, current_step=current_step, user_answers=user_answers)
            else:
                # All steps completed, show outcome
                cursor.execute("SELECT * FROM scenario_outcomes WHERE scenario_id = ?", (scenario_id,))
                outcome_row = cursor.fetchone()
                outcome = dict(outcome_row) if outcome_row else None
                
                cursor.close()
                conn.close()
                
                if outcome:
                    return render_template('scenario_outcome.html', scenario=scenario, outcome=outcome, user_answers=user_answers)
                else:
                    flash('Scenario outcome not found')
        except sqlite3.Error as e:
            flash('Error loading scenario')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return redirect(url_for('scenario_chains'))

@app.route('/submit_scenario_step/<int:scenario_id>/<int:step_number>', methods=['POST'])
def submit_scenario_step(scenario_id, step_number):
    """Handle scenario step submission"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_answer = request.form.get('answer')
    
    # Store answer
    if f'scenario_{scenario_id}_answers' not in session:
        session[f'scenario_{scenario_id}_answers'] = {}
    session[f'scenario_{scenario_id}_answers'][str(step_number)] = user_answer
    
    # Move to next step
    session[f'scenario_{scenario_id}_step'] = step_number + 1
    
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get scenario info
            cursor.execute("SELECT id, domain, law_involved, title FROM scenario_chains WHERE id = ?", (scenario_id,))
            scenario = dict(cursor.fetchone())
            
            # Get current step details
            cursor.execute("SELECT * FROM scenario_steps WHERE scenario_id = ? AND step_number = ?", (scenario_id, step_number))
            step = dict(cursor.fetchone())
            
            is_correct = (user_answer == step['correct_answer'])
            
            # Check if there's a next step
            cursor.execute("SELECT COUNT(*) FROM scenario_steps WHERE scenario_id = ? AND step_number = ?", (scenario_id, step_number + 1))
            has_next = cursor.fetchone()[0] > 0
            
            cursor.close()
            conn.close()
            
            return render_template('scenario_feedback.html', scenario=scenario, step=step, user_answer=user_answer, is_correct=is_correct, has_next=has_next, scenario_id=scenario_id)
        except sqlite3.Error as e:
            flash('Error processing answer')
            print(f"Error: {e}")
            if conn:
                conn.close()
    
    return redirect(url_for('play_scenario', scenario_id=scenario_id))

@app.route('/reset_scenario/<int:scenario_id>')
def reset_scenario(scenario_id):
    """Reset a scenario to start from beginning"""
    if 'user_id' in session:
        session[f'scenario_{scenario_id}_step'] = 1
        session[f'scenario_{scenario_id}_answers'] = {}
    return redirect(url_for('play_scenario', scenario_id=scenario_id))











# Initialize database for all environments
init_db()

# Vercel serverless handler
app.debug = False

# Vercel serverless function handler - this will be called by Vercel
app.debug = False

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
