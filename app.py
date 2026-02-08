from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Database setup for local development
DB_FILE = 'law_game.db'

def get_db_connection():
    try:
        print(f"Attempting to connect to database: {DB_FILE}")
        
        # Ensure database exists
        if not os.path.exists(DB_FILE):
            print(f"Database not found, creating at {DB_FILE}")
            from init_db import init_database
            init_database()
        
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        print("Database connection successful")
        
        # Test connection
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Database has {user_count} users")
        
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    try:
        if not os.path.exists(DB_FILE):
            print(f"Database not found at {DB_FILE}, initializing...")
            from init_db import init_database
            init_database()
            print("Database initialized successfully")
        else:
            print(f"Database found at {DB_FILE}")
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
            
            print(f"Login attempt: username={username}")
            print(f"Request form data: {dict(request.form)}")
            
            if not username or not password:
                print("Missing username or password")
                flash('Please enter both username and password')
                return render_template('login.html')
            
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
                    user_row = cursor.fetchone()
                    
                    print(f"Database query result: {user_row}")
                    
                    if user_row:
                        user = dict(user_row)
                        print(f"User found: {user}")
                        if user['password'] == password:
                            session['user_id'] = user['id']
                            session['username'] = user['username']
                            print(f"Login successful for {username}")
                            print(f"Session data: {dict(session)}")
                            print(f"Redirecting to mode_select")
                            return redirect(url_for('mode_select'))
                        else:
                            print("Password mismatch")
                            flash('Invalid username or password')
                    else:
                        print("User not found")
                        flash('Invalid username or password')
                except Exception as e:
                    print(f"Login query error: {e}")
                    flash('Database error occurred')
                finally:
                    conn.close()
            else:
                print("Database connection failed")
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('mode_select.html')

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
                
                # Get total questions
                cursor.execute("SELECT COUNT(*) FROM bot_questions")
                total_questions = cursor.fetchone()[0]
                
                # Get answered questions for this user
                cursor.execute("SELECT COUNT(*) FROM user_bot_progress WHERE user_id = ?", (user_id,))
                answered_questions = cursor.fetchone()[0]
                
                remaining_questions = total_questions - answered_questions
                
                print(f"Bot mode stats: total={total_questions}, answered={answered_questions}, remaining={remaining_questions}")
                
                # Always show question selection unless no questions remaining
                if remaining_questions > 0:
                    return render_template('bot_question_selection.html', 
                                         total_questions=total_questions,
                                         answered_questions=answered_questions,
                                         remaining_questions=remaining_questions)
                else:
                    # Show completion page
                    cursor.execute("""
                        SELECT ubp.is_correct, bq.correct_answer, bq.explanation, bq.question_text, bq.option_a, bq.option_b, bq.option_c, bq.option_d
                        FROM user_bot_progress ubp
                        JOIN bot_questions bq ON ubp.question_id = bq.id
                        WHERE ubp.user_id = ?
                    """, (user_id,))
                    results = cursor.fetchall()
                    
                    total_answered = len(results)
                    correct_answers = sum(1 for r in results if r[0] == 1)
                    user_score = correct_answers * 3  # 3 points per correct answer
                    
                    return render_template('bot_completion.html', 
                                         total_answered=total_answered,
                                         correct_answers=correct_answers,
                                         user_score=user_score,
                                         total_questions=total_questions)
            except Exception as e:
                print(f"Bot mode query error: {e}")
                flash('Error loading bot mode')
            finally:
                conn.close()
        
        return redirect(url_for('mode_select'))
    except Exception as e:
        print(f"Bot mode route error: {e}")
        return redirect(url_for('mode_select'))

@app.route('/scenario_chains')
def scenario_chains():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get all scenarios
            cursor.execute("SELECT id, domain, law_involved, title FROM scenario_chains")
            scenarios = [dict(row) for row in cursor.fetchall()]
            
            # Get completed scenarios for this user
            cursor.execute("SELECT scenario_id FROM user_scenario_progress WHERE user_id = ? AND completed = 1", (user_id,))
            completed_scenarios = {row['scenario_id'] for row in cursor.fetchall()}
            
            # Add completion status to each scenario
            for scenario in scenarios:
                scenario['completed'] = scenario['id'] in completed_scenarios
            
            return render_template('scenario_chains.html', scenarios=scenarios)
        except Exception as e:
            print(f"Scenario chains error: {e}")
            flash('Error loading scenarios')
        finally:
            conn.close()
    
    return redirect(url_for('mode_select'))

@app.route('/play_scenario/<int:scenario_id>')
def play_scenario(scenario_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Start a new scenario session
    session['current_scenario_id'] = scenario_id
    session['current_question_number'] = 1
    session['scenario_answers'] = []
    
    return redirect(url_for('show_scenario_question', scenario_id=scenario_id, question_number=1))

@app.route('/show_scenario_question/<int:scenario_id>/<int:question_number>')
def show_scenario_question(scenario_id, question_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get scenario info
            cursor.execute("SELECT * FROM scenario_chains WHERE id = ?", (scenario_id,))
            scenario = dict(cursor.fetchone())
            
            # Get the current question/step
            cursor.execute("SELECT * FROM scenario_steps WHERE scenario_id = ? AND step_number = ?", (scenario_id, question_number))
            question_data = cursor.fetchone()
            
            if question_data:
                question = dict(question_data)
                return render_template('scenario_question.html', 
                                     scenario=scenario, 
                                     question=question,
                                     question_number=question_number)
            else:
                # No more questions, show completion
                return render_template('scenario_complete.html',
                                     scenario=scenario,
                                     answers=session.get('scenario_answers', []))
                
        except Exception as e:
            print(f"Show scenario question error: {e}")
            flash('Error loading question')
        finally:
            conn.close()
    
    return redirect(url_for('scenario_chains'))

@app.route('/play_level/<int:level_id>')
def play_level(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM levels WHERE id = ?", (level_id,))
            level = dict(cursor.fetchone())
            
            cursor.execute("SELECT * FROM questions WHERE level_id = ?", (level_id,))
            questions = [dict(row) for row in cursor.fetchall()]
            
            return render_template('play_level.html', level=level, questions=questions)
        except Exception as e:
            print(f"Play level error: {e}")
            flash('Error loading level')
        finally:
            conn.close()
    
    return redirect(url_for('levels'))

@app.route('/start_bot_session', methods=['POST'])
def start_bot_session():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    question_count = int(request.form.get('question_count', 5))  # Default 5 questions
    shuffle = request.form.get('shuffle', 'off')
    
    print(f"Starting bot session: user_id={user_id}, questions={question_count}, shuffle={shuffle}")
    
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get multiple unanswered questions based on user's choice
            if shuffle == 'on':
                cursor.execute("""
                    SELECT bq.* FROM bot_questions bq 
                    LEFT JOIN user_bot_progress ubp ON bq.id = ubp.question_id AND ubp.user_id = ?
                    WHERE ubp.question_id IS NULL 
                    ORDER BY RANDOM() 
                    LIMIT ?
                """, (user_id, question_count))
            else:
                cursor.execute("""
                    SELECT bq.* FROM bot_questions bq 
                    LEFT JOIN user_bot_progress ubp ON bq.id = ubp.question_id AND ubp.user_id = ?
                    WHERE ubp.question_id IS NULL 
                    ORDER BY bq.id 
                    LIMIT ?
                """, (user_id, question_count))
            
            questions = cursor.fetchall()
            
            if questions:
                # Store session questions and scoring in session
                session['bot_session_questions'] = [dict(q) for q in questions]
                session['current_question_index'] = 0
                session['total_session_questions'] = len(questions)
                
                # Initialize scoring
                session['user_score'] = 0
                session['bot_score'] = 0
                session['question_attempts'] = {}  # Track attempts per question
                session['session_start_time'] = str(datetime.now())
                
                print(f"Started session with {len(questions)} questions")
                
                # Generate AI answer for the first question
                import random
                ai_accuracy = 0.8
                first_question = session['bot_session_questions'][0]
                
                if random.random() < ai_accuracy:
                    ai_answer = first_question['correct_answer']
                    ai_is_correct = True
                else:
                    options = ['A', 'B', 'C', 'D']
                    wrong_options = [opt for opt in options if opt != first_question['correct_answer']]
                    ai_answer = random.choice(wrong_options)
                    ai_is_correct = False
                
                return render_template('bot_mode.html', 
                                     question=first_question,
                                     question_number=1,
                                     total_questions=len(questions),
                                     user_score=0,
                                     bot_score=0,
                                     ai_answer=ai_answer,
                                     is_ai_correct=ai_is_correct,
                                     show_result=False)
            else:
                # All questions answered, show results
                print("All questions answered, showing results")
                return redirect(url_for('bot_results'))
                
        except Exception as e:
            print(f"Start bot session error: {e}")
            flash('Error starting bot session')
        finally:
            conn.close()
    else:
        print("Database connection failed")
        flash('Database connection failed')
    
    return redirect(url_for('bot_mode'))

@app.route('/submit_bot_answer', methods=['POST'])
def submit_bot_answer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Debug: Print all form data
    print(f"Form data received: {dict(request.form)}")
    
    question_id = request.form.get('question_id')
    selected_answer = request.form.get('answer')
    
    print(f"Bot answer submission: user_id={user_id}, question_id={question_id}, answer={selected_answer}")
    
    if not question_id or not selected_answer:
        print("Missing question_id or answer")
        flash('Please select an answer')
        return redirect(url_for('bot_mode'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get the correct answer and question details
            cursor.execute("SELECT * FROM bot_questions WHERE id = ?", (question_id,))
            question_row = cursor.fetchone()
            
            if question_row:
                question = dict(question_row)
                correct_answer = question['correct_answer']
                is_correct = selected_answer == correct_answer
                
                print(f"Correct answer: {correct_answer}, Selected: {selected_answer}, Is correct: {is_correct}")
                
                # Track attempts for this question
                if 'question_attempts' not in session:
                    session['question_attempts'] = {}
                session['question_attempts'][question_id] = session['question_attempts'].get(question_id, 0) + 1
                attempts = session['question_attempts'][question_id]
                
                # Generate AI answer and calculate scores
                import random
                ai_accuracy = 0.8  # AI gets 80% of questions correct
                
                # Generate AI answer
                if random.random() < ai_accuracy:
                    ai_answer = correct_answer  # AI gets it right
                    ai_is_correct = True
                else:
                    # AI gets it wrong - pick a wrong option
                    options = ['A', 'B', 'C', 'D']
                    wrong_options = [opt for opt in options if opt != correct_answer]
                    ai_answer = random.choice(wrong_options)
                    ai_is_correct = False
                
                print(f"AI answer: {ai_answer}, Correct: {ai_is_correct}")
                
                # Calculate points
                if is_correct:
                    if attempts == 1:
                        user_points = 3
                    elif attempts == 2:
                        user_points = 2
                    elif attempts == 3:
                        user_points = 1
                    else:
                        user_points = 0
                else:
                    user_points = 0
                
                # AI gets points if correct and hasn't been awarded for this question yet
                bot_points = 0
                if ai_is_correct:
                    # Check if AI already got points for this question
                    if 'ai_awarded_questions' not in session:
                        session['ai_awarded_questions'] = []
                    
                    if question_id not in session['ai_awarded_questions']:
                        bot_points = 3  # AI gets 3 points for correct answer
                        session['ai_awarded_questions'].append(question_id)
                        print(f"AI awarded {bot_points} points for question {question_id}")
                
                # Update scores
                session['user_score'] = session.get('user_score', 0) + user_points
                session['bot_score'] = session.get('bot_score', 0) + bot_points
                
                print(f"Score update: User +{user_points}, Bot +{bot_points}")
                print(f"Current scores: User={session['user_score']}, Bot={session['bot_score']}")
                
                # Record the answer (only record if correct to avoid duplicates)
                if is_correct:
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_bot_progress (user_id, question_id, answered_at, is_correct)
                        VALUES (?, ?, datetime('now'), ?)
                    """, (user_id, question_id, 1))
                    conn.commit()
                
                print("Answer processed successfully")
                
                # Check if we're in a session
                if 'bot_session_questions' in session:
                    current_index = session['current_question_index']
                    total_questions = session['total_session_questions']
                    user_score = session['user_score']
                    bot_score = session['bot_score']
                    
                    if is_correct:
                        # Move to next question if correct
                        current_index += 1
                        
                        if current_index < total_questions:
                            # Show next question
                            session['current_question_index'] = current_index
                            next_question = session['bot_session_questions'][current_index]
                            
                            # Generate AI answer for next question
                            import random
                            ai_accuracy = 0.8
                            
                            if random.random() < ai_accuracy:
                                ai_answer = next_question['correct_answer']
                                ai_is_correct = True
                            else:
                                options = ['A', 'B', 'C', 'D']
                                wrong_options = [opt for opt in options if opt != next_question['correct_answer']]
                                ai_answer = random.choice(wrong_options)
                                ai_is_correct = False
                            
                            return render_template('bot_mode.html', 
                                                 question=next_question,
                                                 question_number=current_index + 1,
                                                 total_questions=total_questions,
                                                 user_score=user_score,
                                                 bot_score=bot_score,
                                                 ai_answer=ai_answer,
                                                 is_ai_correct=ai_is_correct,
                                                 show_result=False)
                        else:
                            # Session complete, show results
                            final_user_score = session['user_score']
                            final_bot_score = session['bot_score']
                            
                            session.pop('bot_session_questions', None)
                            session.pop('current_question_index', None)
                            session.pop('total_session_questions', None)
                            
                            return redirect(url_for('bot_results', user_score=final_user_score, bot_score=final_bot_score))
                    else:
                        # Wrong answer - show feedback with same question
                        return render_template('bot_mode.html',
                                             previous_question=question,
                                             user_answer=selected_answer,
                                             is_user_correct=is_correct,
                                             ai_answer=ai_answer,
                                             is_ai_correct=ai_is_correct,
                                             correct_answer=correct_answer,
                                             show_result=True,
                                             question_number=session.get('current_question_index', 1),
                                             total_questions=session.get('total_session_questions', 1),
                                             user_score=session.get('user_score', 0),
                                             bot_score=session.get('bot_score', 0))
                else:
                    # Not in a session, show feedback and continue
                    return render_template('bot_feedback.html', 
                                         question=question,
                                         selected_answer=selected_answer,
                                         correct_answer=correct_answer,
                                         ai_answer=ai_answer,
                                         is_ai_correct=ai_is_correct,
                                         is_correct=is_correct)
            else:
                print("Question not found")
                flash('Question not found')
                return redirect(url_for('bot_mode'))
            
        except Exception as e:
            print(f"Submit bot answer error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error submitting answer: {str(e)}')
            return redirect(url_for('bot_mode'))
        finally:
            conn.close()
    else:
        print("Database connection failed")
        flash('Database connection failed')
        return redirect(url_for('bot_mode'))

@app.route('/submit_level/<int:level_id>', methods=['POST'])
def submit_level(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Get all form data (answers)
    answers = {}
    for key in request.form:
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            answers[question_id] = request.form[key]
    
    print(f"Level submission: level_id={level_id}, answers={answers}")
    
    if not answers:
        flash('Please answer all questions')
        return redirect(url_for('play_level', level_id=level_id))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get detailed results with explanations
            results = []
            total_questions = len(answers)
            correct_answers = 0
            
            for question_id, selected_answer in answers.items():
                cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
                question_row = cursor.fetchone()
                
                if not question_row:
                    print(f"Question not found: {question_id}")
                    flash(f'Question {question_id} not found')
                    return redirect(url_for('play_level', level_id=level_id))
                
                question = dict(question_row)
                is_correct = selected_answer == question['correct_answer']
                if is_correct:
                    correct_answers += 1
                
                results.append({
                    'question': question,
                    'user_answer': selected_answer,
                    'selected_answer': selected_answer,
                    'is_correct': is_correct,
                    'question_text': question['question_text'],
                    'explanation': question['explanation'],
                    'correct_answer': question['correct_answer'],
                    'options': {
                        'A': question['option_a'],
                        'B': question['option_b'],
                        'C': question['option_c'],
                        'D': question['option_d']
                    }
                })
            
            score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
            
            # Update user progress
            cursor.execute("""
                INSERT OR REPLACE INTO user_progress (user_id, level_id, score, completed, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (user_id, level_id, score, 1 if score >= 60 else 0))
            conn.commit()
            
            print(f"Level completed: score={score}%")
            
            # Show detailed results
            cursor.execute("SELECT * FROM levels WHERE id = ?", (level_id,))
            level = dict(cursor.fetchone())
            
            return render_template('play_level.html', 
                                 level=level, 
                                 results=results,
                                 show_results=True,
                                 score=score,
                                 correct_answers=correct_answers,
                                 total_questions=total_questions)
            
        except Exception as e:
            print(f"Submit level error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error submitting level: {str(e)}')
        finally:
            conn.close()
    
    return redirect(url_for('levels'))

@app.route('/submit_scenario_answer/<int:scenario_id>/<int:question_number>', methods=['POST'])
def submit_scenario_answer(scenario_id, question_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    selected_answer = request.form.get('answer')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get current question data
            cursor.execute("SELECT * FROM scenario_steps WHERE scenario_id = ? AND step_number = ?", (scenario_id, question_number))
            question = dict(cursor.fetchone())
            
            # Check if answer is correct
            is_correct = selected_answer == question['correct_answer']
            
            # Store the answer
            if 'scenario_answers' not in session:
                session['scenario_answers'] = []
            session['scenario_answers'].append({
                'question_number': question_number,
                'question_text': question['story_context'],
                'selected_answer': selected_answer,
                'correct_answer': question['correct_answer'],
                'is_correct': is_correct
            })
            
            # Show feedback
            return render_template('scenario_feedback.html',
                                 scenario_id=scenario_id,
                                 question_number=question_number,
                                 question=question,
                                 selected_answer=selected_answer,
                                 is_correct=is_correct)
                
        except Exception as e:
            print(f"Submit scenario answer error: {e}")
            flash('Error submitting answer')
        finally:
            conn.close()
    
    return redirect(url_for('play_scenario', scenario_id=scenario_id))

@app.route('/continue_scenario/<int:scenario_id>/<int:question_number>')
def continue_scenario(scenario_id, question_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    next_question = question_number + 1
    
    # Check if there are more questions
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scenario_steps WHERE scenario_id = ? AND step_number = ?", (scenario_id, next_question))
            has_next = cursor.fetchone()[0] > 0
            
            if has_next:
                return redirect(url_for('show_scenario_question', scenario_id=scenario_id, question_number=next_question))
            else:
                # Scenario complete - record completion and show completion page
                cursor.execute("SELECT * FROM scenario_chains WHERE id = ?", (scenario_id,))
                scenario = dict(cursor.fetchone())
                
                # Record scenario completion in database
                user_id = session['user_id']
                cursor.execute("""
                    INSERT OR REPLACE INTO user_scenario_progress (user_id, scenario_id, completed, completed_at)
                    VALUES (?, ?, 1, datetime('now'))
                """, (user_id, scenario_id))
                conn.commit()
                print(f"Scenario {scenario_id} marked as completed for user {user_id}")
                
                return render_template('scenario_complete.html',
                                     scenario=scenario,
                                     answers=session.get('scenario_answers', []))
                
        except Exception as e:
            print(f"Continue scenario error: {e}")
            flash('Error continuing scenario')
        finally:
            conn.close()
    
    return redirect(url_for('scenario_chains'))

@app.route('/play_scenario_step/<int:scenario_id>/<int:step_number>')
def play_scenario_step(scenario_id, step_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get scenario info
            cursor.execute("SELECT * FROM scenario_chains WHERE id = ?", (scenario_id,))
            scenario = dict(cursor.fetchone())
            
            # Get the specific step
            cursor.execute("SELECT * FROM scenario_steps WHERE scenario_id = ? AND step_number = ?", (scenario_id, step_number))
            current_step_data = cursor.fetchone()
            
            if current_step_data:
                current_step = dict(current_step_data)
                return render_template('play_scenario.html', 
                                     scenario=scenario, 
                                     current_step=current_step,
                                     step_number=step_number)
            else:
                # No more steps, show outcome
                cursor.execute("SELECT * FROM scenario_outcomes WHERE scenario_id = ?", (scenario_id,))
                outcome = dict(cursor.fetchone())
                return render_template('scenario_outcome.html',
                                     scenario_id=scenario_id,
                                     outcome=outcome)
                
        except Exception as e:
            print(f"Play scenario step error: {e}")
            flash('Error loading scenario step')
        finally:
            conn.close()
    
    return redirect(url_for('scenario_chains'))

@app.route('/show_scenario_outcome/<int:scenario_id>')
def show_scenario_outcome(scenario_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get outcome
            cursor.execute("SELECT * FROM scenario_outcomes WHERE scenario_id = ?", (scenario_id,))
            outcome = dict(cursor.fetchone())
            
            return render_template('scenario_outcome.html',
                                 scenario_id=scenario_id,
                                 outcome=outcome)
                
        except Exception as e:
            print(f"Show scenario outcome error: {e}")
            flash('Error loading outcome')
        finally:
            conn.close()
    
    return redirect(url_for('scenario_chains'))

@app.route('/retry_same_question', methods=['POST'])
def retry_same_question():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    question_id = request.form.get('question_id')
    
    print(f"Retry same question: question_id={question_id}")
    
    if 'bot_session_questions' in session and question_id:
        # Find the question in the session and show it again
        for question in session['bot_session_questions']:
            if str(question['id']) == str(question_id):
                current_index = session['current_question_index']
                total_questions = session['total_session_questions']
                user_score = session.get('user_score', 0)
                bot_score = session.get('bot_score', 0)
                
                print(f"Found question for retry, current scores: User={user_score}, Bot={bot_score}")
                
                return render_template('bot_mode.html', 
                                     question=question,
                                     question_number=current_index + 1,
                                     total_questions=total_questions,
                                     user_score=user_score,
                                     bot_score=bot_score)
    
    print("Question not found for retry, falling back to bot_mode")
    # Fallback to bot_mode
    return redirect(url_for('bot_mode'))

@app.route('/continue_bot_session', methods=['POST'])
def continue_bot_session():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    print("Continue bot session called")
    
    # Check if we're in a session
    if 'bot_session_questions' in session:
        current_index = session['current_question_index']
        total_questions = session['total_session_questions']
        user_score = session.get('user_score', 0)
        bot_score = session.get('bot_score', 0)
        
        print(f"Session data: current_index={current_index}, total={total_questions}")
        
        # Move to next question
        current_index += 1
        
        if current_index < total_questions:
            # Show next question
            session['current_question_index'] = current_index
            next_question = session['bot_session_questions'][current_index]
            
            print(f"Moving to next question: {current_index + 1} of {total_questions}")
            
            return render_template('bot_mode.html', 
                                 question=next_question,
                                 question_number=current_index + 1,
                                 total_questions=total_questions,
                                 user_score=user_score,
                                 bot_score=bot_score)
        else:
            # Session complete, show results
            final_user_score = session.get('user_score', 0)
            final_bot_score = session.get('bot_score', 0)
            
            print(f"Session complete, final scores: User={final_user_score}, Bot={final_bot_score}")
            
            session.pop('bot_session_questions', None)
            session.pop('current_question_index', None)
            session.pop('total_session_questions', None)
            
            return redirect(url_for('bot_results', user_score=final_user_score, bot_score=final_bot_score))
    else:
        print("Not in a session, getting random question")
        # Not in a session, get a random question
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT bq.* FROM bot_questions bq 
                    LEFT JOIN user_bot_progress ubp ON bq.id = ubp.question_id AND ubp.user_id = ?
                    WHERE ubp.question_id IS NULL 
                    ORDER BY RANDOM() 
                    LIMIT 1
                """, (user_id,))
                next_question = cursor.fetchone()
                
                if next_question:
                    next_question_dict = dict(next_question)
                    return render_template('bot_mode.html', question=next_question_dict)
                else:
                    # No more questions, show final results
                    return redirect(url_for('bot_results'))
                
            except Exception as e:
                print(f"Continue bot session error: {e}")
                flash('Error getting next question')
                return redirect(url_for('bot_mode'))
            finally:
                conn.close()
    
    return redirect(url_for('bot_mode'))

@app.route('/bot_results')
def bot_results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    print(f"Bot results called for user: {user_id}")
    
    # Get scores from URL parameters or session
    user_score = request.args.get('user_score', type=int) or session.get('user_score', 0)
    bot_score = request.args.get('bot_score', type=int) or session.get('bot_score', 0)
    
    print(f"Scores: User={user_score}, Bot={bot_score}")
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get user's bot progress with details
            cursor.execute("""
                SELECT ubp.is_correct, bq.correct_answer, bq.explanation, bq.question_text, bq.option_a, bq.option_b, bq.option_c, bq.option_d
                FROM user_bot_progress ubp
                JOIN bot_questions bq ON ubp.question_id = bq.id
                WHERE ubp.user_id = ?
            """, (user_id,))
            results = cursor.fetchall()
            
            total_answered = len(results)
            correct_answers = sum(1 for r in results if r[0] == 1)
            
            # Check if all questions are completed
            cursor.execute("SELECT COUNT(*) FROM bot_questions")
            total_questions = cursor.fetchone()[0]
            all_completed = total_answered >= total_questions
            
            print(f"Database results: {total_answered} questions, {correct_answers} correct, all_completed: {all_completed}")
            
            # Structure data for template
            questions = []
            user_answers = []
            ai_answers = []
            
            for r in results:
                # Question data
                questions.append({
                    'question_text': r[3],
                    'correct_answer': r[1],
                    'explanation': r[2]
                })
                
                # User answer data - simulate based on correctness
                if r[0] == 1:  # Correct answer
                    user_answer = r[1]  # User gave correct answer
                else:  # Wrong answer - pick a wrong option
                    options = [r[4], r[5], r[6], r[7]]
                    wrong_options = [opt for opt in options if opt != r[1]]
                    user_answer = wrong_options[0] if wrong_options else 'A'
                
                user_answers.append({
                    'answer': user_answer,
                    'is_correct': r[0] == 1
                })
                
                # AI answer data (simulate AI response - AI gets it right)
                ai_answers.append({
                    'answer': r[1],  # AI gives correct answer
                    'is_correct': True
                })
            
            # Calculate total possible points
            total_possible_points = total_answered * 3
            
            return render_template('bot_results.html', 
                                 questions=questions,
                                 user_answers=user_answers,
                                 ai_answers=ai_answers,
                                 user_score=user_score,
                                 ai_score=bot_score,
                                 total_questions=total_answered,
                                 total_possible_points=total_possible_points,
                                 all_completed=all_completed)
            
        except Exception as e:
            print(f"Bot results error: {e}")
            import traceback
            traceback.print_exc()
            flash('Error loading results')
            return redirect(url_for('bot_mode'))
        finally:
            conn.close()
    else:
        print("Database connection failed for bot results")
        flash('Database connection failed')
        return redirect(url_for('bot_mode'))

@app.route('/reset_bot_questions')
def reset_bot_questions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_bot_progress WHERE user_id = ?", (user_id,))
            conn.commit()
            flash('Bot progress reset successfully')
        except Exception as e:
            print(f"Reset bot questions error: {e}")
            flash('Error resetting progress')
        finally:
            conn.close()
    
    return redirect(url_for('bot_mode'))

@app.route('/reset_scenario/<int:scenario_id>')
def reset_scenario(scenario_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return redirect(url_for('play_scenario', scenario_id=scenario_id))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)