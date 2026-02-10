"""Initialize SQLite database with schema and sample data"""
import sqlite3
import os

DB_FILE = 'law_game.db'

def init_database():
    """Create database tables and insert sample data"""
    # Remove existing database if it exists (for fresh start)
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("Removed existing database")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    print("Creating tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Levels table
    cursor.execute('''
        CREATE TABLE levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_number INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Questions table
    cursor.execute('''
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL
        )
    ''')
    
    # User progress table
    cursor.execute('''
        CREATE TABLE user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, level_id)
        )
    ''')
    
    # Bot questions table
    cursor.execute('''
        CREATE TABLE bot_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scenario chains table
    cursor.execute('''
        CREATE TABLE scenario_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            law_involved TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scenario steps table
    cursor.execute('''
        CREATE TABLE scenario_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            story_context TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            feedback TEXT NOT NULL,
            FOREIGN KEY (scenario_id) REFERENCES scenario_chains(id)
        )
    ''')
    
    # Scenario outcomes table
    cursor.execute('''
        CREATE TABLE scenario_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER NOT NULL,
            final_outcome TEXT NOT NULL,
            learning_summary TEXT NOT NULL,
            FOREIGN KEY (scenario_id) REFERENCES scenario_chains(id)
        )
    ''')
    
    # User bot progress table
    cursor.execute('''
        CREATE TABLE user_bot_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_correct INTEGER DEFAULT 0,
            UNIQUE(user_id, question_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES bot_questions(id)
        )
    ''')
    
    # User scenario progress table
    cursor.execute('''
        CREATE TABLE user_scenario_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scenario_id INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, scenario_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (scenario_id) REFERENCES scenario_chains(id)
        )
    ''')
    

    # Insert sample levels
    print("Inserting sample data...")
    levels = [
        (1, 'Introduction to Law', 'Learn the basics of legal principles and terminology'),
        (2, 'Contract Law Fundamentals', 'Understand the essentials of contract formation and enforcement'),
        (3, 'Criminal Law Basics', 'Explore fundamental concepts in criminal law'),
        (4, 'Property Law', 'Learn about property rights and ownership'),
        (5, 'Constitutional Law', 'Study the principles of constitutional governance')
    ]
    cursor.executemany('INSERT INTO levels (level_number, title, description) VALUES (?, ?, ?)', levels)
    
    # Insert sample questions for Level 1
    questions_level1 = [
        (1, 'What is the primary purpose of law in society?', 'To generate revenue for government', 'To restrict individual freedom', 'To maintain order and protect rights', 'To create confusion', 'C', 'Law serves to maintain social order, protect individual rights, and provide a framework for resolving disputes.'),
        (1, 'What is the difference between civil law and criminal law?', 'Civil law is more serious than criminal law', 'Criminal law only applies to corporations', 'There is no difference', 'Civil law deals with disputes between individuals, criminal law deals with offenses against society', 'D', 'Civil law resolves disputes between parties while criminal law addresses offenses against society.'),
        (1, 'What does "precedent" mean in legal context?', 'A warning before arrest', 'A type of legal document', 'A previous court decision used as a guide', 'A court fee', 'C', 'Precedent refers to previous judicial decisions used as authority for future similar cases.'),
        (1, 'What is the burden of proof in a criminal case?', 'Clear and convincing evidence', 'Probable cause', 'Preponderance of evidence', 'Beyond a reasonable doubt', 'D', 'In criminal cases, guilt must be proven beyond a reasonable doubt.'),
        (1, 'What is a statute?', 'A legal contract', 'A type of lawsuit', 'A court decision', 'A written law passed by a legislative body', 'D', 'A statute is a formal written law enacted by a legislative body.')
    ]
    cursor.executemany('INSERT INTO questions (level_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', questions_level1)
    
    # Insert sample questions for Level 2
    questions_level2 = [
        (2, 'What are the essential elements of a valid contract?', 'Only offer and acceptance', 'Offer, acceptance, consideration, capacity, and legality', 'Only written agreement', 'Just a handshake', 'B', 'A valid contract requires offer, acceptance, consideration, capacity, and legality.'),
        (2, 'What is "consideration" in contract law?', 'A court hearing', 'Thoughtful behavior', 'Something of value exchanged between parties', 'A legal document', 'C', 'Consideration is something of value exchanged between parties.'),
        (2, 'When can a contract be voided due to mistake?', 'Spelling errors', 'Mutual mistake of material fact', 'Any mistake', 'Only mathematical errors', 'B', 'A contract may be voided when both parties share a mutual mistake of material fact.'),
        (2, 'What is a breach of contract?', 'Failure to perform contractual obligations', 'Renegotiating terms', 'Breaking a physical object', 'Signing a contract', 'A', 'A breach occurs when one party fails to fulfill contractual obligations.'),
        (2, 'What are damages in contract law?', 'Contract terms', 'Physical injuries', 'Monetary compensation for breach', 'Legal fees', 'C', 'Damages compensate the injured party for losses from breach.')
    ]
    cursor.executemany('INSERT INTO questions (level_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', questions_level2)
    
    # Insert sample questions for Level 3
    questions_level3 = [
        (3, 'What is the difference between a felony and a misdemeanor?', 'Felonies are more serious crimes with harsher penalties', 'There is no difference', 'Misdemeanors are always violent', 'Felonies cannot be prosecuted', 'A', 'Felonies are serious crimes typically punishable by imprisonment for more than one year, while misdemeanors are less serious offenses with lighter penalties.'),
        (3, 'What is "mens rea" in criminal law?', 'Physical evidence', 'A type of defense', 'A court procedure', 'Guilty mind or criminal intent', 'D', 'Mens rea refers to the mental state or intent required to commit a crime.'),
        (3, 'What is self-defense?', 'Only applicable to police', 'Attacking first', 'Defending property only', 'The right to use reasonable force to protect oneself from harm', 'D', 'Self-defense is a legal justification for using reasonable force to protect oneself or others from imminent harm.'),
        (3, 'What does "beyond a reasonable doubt" mean?', 'A type of evidence', 'The standard of proof required for criminal conviction', 'Absolute certainty', 'A defense strategy', 'B', 'Beyond a reasonable doubt is the highest standard of proof for criminal conviction.'),
        (3, 'What is the difference between murder and manslaughter?', 'Murder requires intent, manslaughter is unlawful killing without malice', 'Manslaughter is more serious', 'Only murder is a crime', 'No difference', 'A', 'Murder is intentional killing with malice aforethought, while manslaughter is unlawful killing without malice.')
    ]
    cursor.executemany('INSERT INTO questions (level_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', questions_level3)
    
    # Insert sample questions for Level 4
    questions_level4 = [
        (4, 'What is real property?', 'Property that is genuine', 'Personal belongings', 'Land and anything permanently attached to it', 'Intellectual property', 'C', 'Real property refers to land and anything permanently attached to it, such as buildings, trees, and minerals. It is immovable property.'),
        (4, 'What is a deed?', 'A type of lease', 'A legal action', 'A property tax', 'A written document that transfers property ownership', 'D', 'A deed is a legal document that transfers ownership of real property from one party (grantor) to another (grantee). It must be in writing and properly executed.'),
        (4, 'What is adverse possession?', 'Renting property', 'Selling property', 'Owning property legally', 'Acquiring property rights through continuous, open, and hostile use', 'D', 'Adverse possession allows someone to gain legal title to property by occupying it continuously, openly, and without permission for a statutory period (typically 7-20 years).'),
        (4, 'What is an easement?', 'A property sale', 'The right to use another person\'s land for a specific purpose', 'Property ownership', 'A type of mortgage', 'B', 'An easement is a legal right to use another person\'s property for a specific purpose, such as a right-of-way for access, without owning the property.'),
        (4, 'What is the difference between joint tenancy and tenancy in common?', 'No difference', 'Joint tenancy includes right of survivorship, tenancy in common does not', 'Tenancy in common is only for businesses', 'Joint tenancy cannot be sold', 'B', 'Joint tenancy includes the right of survivorship (when one owner dies, their share goes to other owners), while tenancy in common allows owners to pass their share to heirs.')
    ]
    cursor.executemany('INSERT INTO questions (level_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', questions_level4)
    
    # Insert sample questions for Level 5
    questions_level5 = [
        (5, 'What is the purpose of separation of powers?', 'To create confusion', 'To divide government into branches', 'To increase government size', 'To prevent any one branch from becoming too powerful', 'C', 'Separation of powers divides government into executive, legislative, and judicial branches, each with distinct powers, to prevent tyranny and protect liberty through checks and balances.'),
        (5, 'What are constitutional rights?', 'Fundamental rights protected by the constitution', 'Rights granted by states only', 'Rights that can be easily revoked', 'Only economic rights', 'A', 'Constitutional rights are fundamental rights and freedoms guaranteed by the constitution, such as freedom of speech, religion, and due process, which are protected from government infringement.'),
        (5, 'What is judicial review?', 'Reviewing court cases', 'The power of courts to review and invalidate laws that violate the constitution', 'A type of appeal', 'Reviewing legal documents', 'B', 'Judicial review is the power of courts to examine laws and government actions to determine if they comply with the constitution, and to strike them down if they do not.'),
        (5, 'What is federalism?', 'A type of government', 'Division of power between national and state governments', 'Only national government', 'Only state government', 'D', 'Federalism is a system of government where power is divided between a central (federal) government and regional (state) governments, each with their own areas of authority.'),
        (5, 'What does "due process" mean?', 'Administrative processes', 'Only criminal procedures', 'Quick legal procedures', 'Fair legal procedures and protection of individual rights', 'C', 'Due process requires that the government follow fair and established legal procedures when depriving a person of life, liberty, or property, ensuring fundamental fairness and protection of rights.')
    ]
    cursor.executemany('INSERT INTO questions (level_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', questions_level5)
    
    # Insert sample bot questions
    bot_questions = [
        ('In a contract dispute, what is the statute of limitations typically?', '1 year', '10 years', '3-6 years depending on jurisdiction and contract type', 'No time limit', 'C', 'Statutes of limitations vary by jurisdiction and contract type, but typically range from 3-6 years for written contracts and 2-4 years for oral contracts.'),
        ('What is "double jeopardy" in criminal law?', 'Being tried twice for the same crime', 'Committing two crimes', 'A type of defense', 'A court procedure', 'A', 'Double jeopardy prevents a person from being tried twice for the same offense after being acquitted or convicted.'),
        ('What is a "tort" in legal terms?', 'A criminal offense', 'A type of contract', 'A property right', 'A civil wrong that causes harm or loss', 'D', 'A tort is a civil wrong (not a crime) that causes harm or loss.'),
        ('What does "habeas corpus" mean?', 'Body of evidence', 'A type of contract', 'A writ requiring a person under arrest to be brought before a judge', 'A property right', 'C', 'Habeas corpus requires authorities to justify the legality of detention.'),
        ('What is "stare decisis"?', 'A court order', 'The legal principle of following precedent', 'A type of lawsuit', 'A legal document', 'B', 'Stare decisis ensures courts follow precedents for consistency.'),
        ('A shop displays MRP but charges more at billing.', 'Tax issue only', 'No offence', 'Consumer law violation', 'Shopkeeper right', 'C', 'Charging above MRP is an unfair trade practice.'),
        ('A person is denied entry to a public place due to religion.', 'Lawful restriction', 'Private decision', 'No issue', 'Discrimination', 'D', 'Discrimination in public places violates constitutional principles.'),
        ('A company stores customer Aadhaar details without consent.', 'Allowed if internal', 'Normal business practice', 'No offence', 'Data protection violation', 'D', 'Collecting sensitive data without consent violates IT rules.'),
        ('A school expels a student without giving any explanation.', 'Normal discipline', 'Violation of natural justice', 'School policy', 'No right involved', 'B', 'Natural justice requires fair hearing and reasons.'),
        ('A police officer uses force on an accused in custody.', 'Custodial violence', 'Allowed for confession', 'Internal matter', 'Disciplinary issue only', 'A', 'Custodial violence violates fundamental rights.'),
        ('A company does not provide maternity leave to a woman employee.', 'Optional benefit', 'No law applies', 'Labour law violation', 'Company policy', 'C', 'Maternity leave is a statutory right.'),
        ('A person posts communal hate speech online.', 'Political opinion', 'Free expression', 'No crime', 'Hate speech offence', 'D', 'Hate speech promoting enmity is punishable.'),
        ('A builder delays possession of a flat by two years.', 'Force majeure always', 'Normal delay', 'No remedy', 'Consumer grievance', 'D', 'Unreasonable delay is a consumer law violation.'),
        ('A person records a private conversation without consent.', 'Privacy violation', 'Journalism', 'Freedom of press', 'No offence', 'A', 'Recording private conversations without consent violates privacy.'),
        ('A government office demands bribe for routine service.', 'Office discretion', 'Corruption offence', 'Administrative fee', 'No law broken', 'B', 'Demanding bribe is punishable under anti-corruption laws.'),
        ('An employer fires an employee for filing a legal complaint.', 'Contract freedom', 'Employer right', 'No protection', 'Unfair labour practice', 'D', 'Employees are protected against retaliation.'),
        ('A person spreads false information causing public panic.', 'Opinion sharing', 'No offence', 'Public mischief', 'Freedom of speech', 'C', 'False information causing panic is punishable.'),
        ('A hospital refuses treatment to an accident victim due to police formalities.', 'Civil matter', 'No law applies', 'Hospital protocol', 'Violation of right to life', 'D', 'Emergency treatment is part of right to life.'),
        ('A company copies another brand\'s logo to confuse customers.', 'Marketing strategy', 'Trademark infringement', 'Fair competition', 'No offence', 'B', 'Deceptive similarity violates trademark law.'),
        ('A landlord cuts electricity to force tenant to vacate.', 'Civil dispute only', 'Owner right', 'Illegal coercion', 'Police issue', 'C', 'Essential services cannot be cut to force eviction.'),
        ('A person refuses to obey lawful orders during a curfew.', 'No offence', 'Violation of lawful order', 'Personal freedom', 'Civil matter', 'B', 'Disobeying lawful orders during emergencies is punishable.'),
        ('A company fails to disclose product side effects.', 'Buyer responsibility', 'Marketing choice', 'Consumer protection violation', 'No issue', 'C', 'Non-disclosure of material facts is unfair trade practice.'),
        ('A person uploads morphed images to defame someone.', 'No offence', 'Creative editing', 'Cyber defamation', 'Copyright issue only', 'C', 'Morphed defamatory images constitute cyber defamation.'),
        ('A public servant refuses to perform official duty without reason.', 'No offence', 'Misconduct', 'Personal choice', 'Internal policy', 'B', 'Public servants must perform official duties.'),
        ('A private company leaks employee medical records.', 'Company right', 'No law applies', 'HR decision', 'Privacy breach', 'D', 'Medical data is protected sensitive information.')
    ]
    cursor.executemany('INSERT INTO bot_questions (question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?)', bot_questions)
    
    # Insert sample scenario chains
    print("Inserting scenario chains...")
    
    # Scenario 1: Consumer Protection - MRP Overcharging
    cursor.execute('INSERT INTO scenario_chains (domain, law_involved, title) VALUES (?, ?, ?)', 
                   ('Consumer', 'Consumer Protection Act', 'Shop Overcharging Above MRP'))
    scenario1_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO scenario_steps (scenario_id, step_number, story_context, option_a, option_b, option_c, option_d, correct_answer, feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (scenario1_id, 1, 
                    'You go to a local shop to buy a product. The price tag shows MRP ₹100, but at the billing counter, the shopkeeper charges you ₹120. You notice this immediately.',
                    'Pay ₹120 without questioning - shopkeepers can charge what they want',
                    'Argue loudly and create a scene in the shop',
                    'Politely point out the MRP and ask for the correct price',
                    'Leave without buying and never return',
                    'C',
                    'Politely pointing out MRP is the correct first step. Under consumer law, charging above MRP is illegal, but maintaining decorum helps resolve the issue.'))
    
    cursor.execute('INSERT INTO scenario_steps (scenario_id, step_number, story_context, option_a, option_b, option_c, option_d, correct_answer, feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (scenario1_id, 2,
                    'The shopkeeper refuses to charge MRP and insists on ₹120. He says "This is my shop, I decide the price." You have the product in your hand and the bill shows ₹120.',
                    'Pay the extra amount to avoid conflict',
                    'Put the product back and leave without taking action',
                    'Pay MRP (₹100) and ask for a proper bill, then file a complaint with consumer forum',
                    'Call the police immediately',
                    'C',
                    'Paying MRP and filing a complaint is the lawful approach. Consumer Protection Act protects you from unfair trade practices like overcharging above MRP.'))
    
    cursor.execute('INSERT INTO scenario_outcomes (scenario_id, final_outcome, learning_summary) VALUES (?, ?, ?)',
                   (scenario1_id,
                    'You file a complaint with the District Consumer Forum. The forum orders the shopkeeper to refund the excess amount and pay compensation. The shopkeeper is also warned against future violations.',
                    'Charging above MRP is an unfair trade practice under Consumer Protection Act. Consumers have the right to pay only the MRP. Always keep bills and file complaints with consumer forums for redressal.'))
    
    # Scenario 2: Labour Law - Maternity Leave
    cursor.execute('INSERT INTO scenario_chains (domain, law_involved, title) VALUES (?, ?, ?)',
                   ('Labour', 'Maternity Benefit Act', 'Denied Maternity Leave'))
    scenario2_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO scenario_steps (scenario_id, step_number, story_context, option_a, option_b, option_c, option_d, correct_answer, feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (scenario2_id, 1,
                    'You are a working woman, 6 months pregnant. You inform your HR department about your pregnancy and request maternity leave as per company policy. HR responds: "Our company doesn\'t provide maternity leave. You can take unpaid leave if you want."',
                    'Accept the unpaid leave and don\'t question it',
                    'Resign from the job immediately',
                    'Inform HR that maternity leave is a legal right and request it in writing',
                    'Ignore HR and continue working',
                    'C',
                    'Maternity leave is a statutory right under the Maternity Benefit Act. Requesting it in writing creates a record and shows you know your rights.'))
    
    cursor.execute('INSERT INTO scenario_steps (scenario_id, step_number, story_context, option_a, option_b, option_c, option_d, correct_answer, feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (scenario2_id, 2,
                    'HR still refuses, saying "It\'s company policy. We don\'t have to follow government laws." You have been working there for 2 years. Your due date is in 3 months.',
                    'Accept the company policy and take unpaid leave',
                    'File a complaint with the Labour Commissioner and continue working until you get a response',
                    'Quit immediately and find another job',
                    'Threaten to sue without taking any formal action',
                    'B',
                    'Filing with Labour Commissioner is the correct legal step. The Maternity Benefit Act applies to all establishments with 10+ employees. You can continue working while the complaint is processed.'))
    
    cursor.execute('INSERT INTO scenario_outcomes (scenario_id, final_outcome, learning_summary) VALUES (?, ?, ?)',
                   (scenario2_id,
                    'The Labour Commissioner orders your company to grant you 26 weeks of paid maternity leave with full salary. The company is also fined for violating labour laws. You receive your entitled benefits.',
                    'Maternity leave is a statutory right, not optional. The Maternity Benefit Act provides 26 weeks of paid leave. Companies cannot deny this right. Always approach Labour Commissioner for violations.'))
    
    # Scenario 3: Cyber Law - Data Protection
    cursor.execute('INSERT INTO scenario_chains (domain, law_involved, title) VALUES (?, ?, ?)',
                   ('Cyber', 'Information Technology Act & IT Rules', 'Unauthorized Aadhaar Data Collection'))
    scenario3_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO scenario_steps (scenario_id, step_number, story_context, option_a, option_b, option_c, option_d, correct_answer, feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (scenario3_id, 1,
                    'You visit a mobile store to buy a new SIM card. The store owner asks for your Aadhaar card and says he needs to keep a copy "for company records." You are unsure if this is necessary.',
                    'Give Aadhaar copy without questioning',
                    'Refuse completely and leave the store',
                    'Ask why they need a copy and check if they are authorized to collect Aadhaar data',
                    'Give a fake Aadhaar number',
                    'C',
                    'Asking questions is important. Aadhaar can only be collected by authorized entities for specific purposes. SIM card activation requires Aadhaar verification, but storing copies may not be necessary.'))
    
    cursor.execute('INSERT INTO scenario_steps (scenario_id, step_number, story_context, option_a, option_b, option_c, option_d, correct_answer, feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (scenario3_id, 2,
                    'The store owner insists on keeping a physical copy of your Aadhaar. You later discover that the store is storing Aadhaar copies of all customers in an unsecured file cabinet, accessible to anyone. You realize this is a data protection violation.',
                    'Ignore it - nothing you can do now',
                    'File a complaint with the Data Protection Authority or Cyber Crime cell about unauthorized data storage',
                    'Go back and demand your Aadhaar copy back',
                    'Post about it on social media only',
                    'B',
                    'Filing a formal complaint is the correct action. Storing Aadhaar data without proper security and authorization violates IT Rules. This puts your personal data at risk.'))
    
    cursor.execute('INSERT INTO scenario_outcomes (scenario_id, final_outcome, learning_summary) VALUES (?, ?, ?)',
                   (scenario3_id,
                    'The Cyber Crime cell investigates and finds the store was storing Aadhaar data without authorization. The store is fined and ordered to securely destroy all unauthorized copies. You are informed about the action taken.',
                    'Aadhaar and sensitive personal data can only be collected by authorized entities with proper security. Unauthorized storage violates IT Rules. Always file complaints with Cyber Crime cells for data protection violations.'))
    

    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Database initialized successfully!")
    print(f"Database file created: {DB_FILE}")

def add_scenario_progress_table():
    """Add scenario progress table to existing database"""
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_scenario_progress'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Adding user_scenario_progress table to existing database...")
            cursor.execute('''
                CREATE TABLE user_scenario_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    scenario_id INTEGER NOT NULL,
                    completed INTEGER DEFAULT 0,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, scenario_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (scenario_id) REFERENCES scenario_chains(id)
                )
            ''')
            conn.commit()
            print("user_scenario_progress table added successfully")
        
        conn.close()

if __name__ == '__main__':
    init_database()
    # Also try to add scenario progress table if database already exists
    add_scenario_progress_table()
