# app.py
# Phishing Awareness Training Platform
# A beginner-friendly educational tool to learn about phishing attacks.
# Uses Flask (Python web framework) and SQLite (lightweight database).

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
# Secret key is required for Flask sessions (used to track quiz/simulation per visitor).
# In production you would load this from an environment variable.
app.secret_key = 'phish-edu-secret-2024'

# Path to the SQLite database file stored in the same folder as app.py
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


# ── Database helpers ──────────────────────────────────────────────────────────
def get_db():
    """Open a connection to the SQLite database and return it."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us access columns by name (row['score'])
    return conn


def init_db():
    """
    Create the database tables if they don't already exist.
    Called once when the application starts.

    Tables:
      quiz_results      – stores each quiz attempt (score, total questions, date)
      simulation_events – records when a user clicks the simulated phishing link
    """
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            score       INTEGER NOT NULL,
            total       INTEGER NOT NULL,
            percentage  REAL    NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS simulation_events (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            action     TEXT    NOT NULL,  -- e.g. 'clicked_link'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()


# ── Quiz questions ────────────────────────────────────────────────────────────
# Each question is a dict with: text, options (A-D), correct answer key,
# and an explanation shown after the quiz.
QUESTIONS = [
    {
        'id': 1,
        'text': 'An email says "Your account will be suspended in 24 hours – click here immediately!" What is this an example of?',
        'options': {
            'A': 'A legitimate security alert',
            'B': 'Urgent/threatening language – a classic phishing tactic',
            'C': 'Normal account maintenance',
            'D': 'A spam advertisement',
        },
        'answer': 'B',
        'explanation': 'Creating false urgency is one of the most common phishing tactics. Attackers pressure you to act before you have time to think critically.',
    },
    {
        'id': 2,
        'text': 'You receive an email from "support@paypa1.com" asking you to verify your account. What should you do?',
        'options': {
            'A': 'Click the link and verify immediately',
            'B': 'Reply with your account details',
            'C': 'Recognise it as phishing – the domain is misspelled (paypa1 ≠ paypal)',
            'D': 'Forward it to your contacts as a warning',
        },
        'answer': 'C',
        'explanation': '"paypa1.com" uses the digit "1" instead of the letter "l" – a typosquatting trick. Always inspect the sender\'s email domain carefully.',
    },
    {
        'id': 3,
        'text': 'A website has a padlock icon and starts with HTTPS. Does this guarantee it is safe?',
        'options': {
            'A': 'Yes – HTTPS means the site is legitimate',
            'B': 'No – HTTPS only encrypts the connection, not the site\'s legitimacy',
            'C': 'Yes – only banks get HTTPS certificates',
            'D': 'No – HTTPS is always fake on phishing sites',
        },
        'answer': 'B',
        'explanation': 'HTTPS encrypts data in transit but does NOT verify that the website is trustworthy. Phishing sites can and do use HTTPS. Always check the domain name.',
    },
    {
        'id': 4,
        'text': 'Someone calls claiming to be IT support and asks for your password to fix a problem. What do you do?',
        'options': {
            'A': 'Give them the password – they are from IT',
            'B': 'Give them a temporary password',
            'C': 'Refuse – legitimate IT staff never need your password',
            'D': 'Ask them to call back later, then give it',
        },
        'answer': 'C',
        'explanation': 'Legitimate IT professionals never need your password. They have admin tools to access systems. This is a classic vishing (voice phishing) attack.',
    },
    {
        'id': 5,
        'text': 'You find a USB drive in the car park. What is the safest action?',
        'options': {
            'A': 'Plug it in to find the owner',
            'B': 'Plug it in at home where it is safer',
            'C': 'Hand it to IT/security without plugging it in',
            'D': 'Format it and keep it',
        },
        'answer': 'C',
        'explanation': 'Attackers deliberately leave infected USB drives (baiting attack). Plugging in an unknown drive can instantly install malware. Always hand it to security personnel.',
    },
]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Dashboard – shows platform intro and summary statistics."""
    conn = get_db()
    # Count total quiz attempts and simulation clicks for the stats panel
    total_quizzes = conn.execute('SELECT COUNT(*) FROM quiz_results').fetchone()[0]
    total_sim_clicks = conn.execute(
        "SELECT COUNT(*) FROM simulation_events WHERE action = 'clicked_link'"
    ).fetchone()[0]
    avg_score_row = conn.execute('SELECT AVG(percentage) FROM quiz_results').fetchone()[0]
    avg_score = round(avg_score_row, 1) if avg_score_row else 0
    conn.close()
    return render_template('index.html',
                           total_quizzes=total_quizzes,
                           total_sim_clicks=total_sim_clicks,
                           avg_score=avg_score)


@app.route('/learn')
def learn():
    """Educational page covering phishing techniques and how to stay safe."""
    return render_template('learn.html')


@app.route('/simulation')
def simulation():
    """
    Safe phishing simulation page.
    Shows a fake-looking 'urgent' email. When the user clicks the button
    they are recorded (no credentials collected) and taken to the result page.
    """
    # Clear any previous simulation flag so the user can re-attempt
    session.pop('sim_clicked', None)
    return render_template('simulation.html')


@app.route('/simulation-click')
def simulation_click():
    """
    Records that the user clicked the simulated phishing link.
    NO passwords, credentials, or personal data are collected here.
    Only a simple event ('clicked_link') is written to the database.
    """
    conn = get_db()
    conn.execute("INSERT INTO simulation_events (action) VALUES ('clicked_link')")
    conn.commit()
    conn.close()
    # Flag in session so the result page knows a click just happened
    session['sim_clicked'] = True
    return redirect(url_for('result'))


@app.route('/result')
def result():
    """
    Training warning page shown after the simulated phishing link is clicked.
    Explains what happened and teaches the user what to look for.
    """
    clicked = session.get('sim_clicked', False)
    return render_template('result.html', clicked=clicked)


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """
    GET  – renders the 5-question multiple-choice quiz.
    POST – collects the answers, calculates the score, saves it, redirects
           to the quiz result page.
    """
    if request.method == 'POST':
        score = 0
        total = len(QUESTIONS)
        user_answers = {}

        for q in QUESTIONS:
            chosen = request.form.get(f'q{q["id"]}', '').upper()
            user_answers[q['id']] = chosen
            if chosen == q['answer']:
                score += 1

        percentage = round((score / total) * 100, 1)

        # Save the attempt to the database (no personal data stored)
        conn = get_db()
        conn.execute(
            'INSERT INTO quiz_results (score, total, percentage) VALUES (?, ?, ?)',
            (score, total, percentage)
        )
        conn.commit()
        conn.close()

        # Store results in session so the result page can display them
        session['quiz_score'] = score
        session['quiz_total'] = total
        session['quiz_percentage'] = percentage
        session['quiz_answers'] = user_answers

        return redirect(url_for('quiz_result'))

    return render_template('quiz.html', questions=QUESTIONS)


@app.route('/quiz-result')
def quiz_result():
    """Displays the score, correct answers, and explanations after the quiz."""
    score = session.get('quiz_score')
    total = session.get('quiz_total')
    percentage = session.get('quiz_percentage')
    user_answers = session.get('quiz_answers', {})

    # If someone visits this URL directly without taking the quiz, redirect them
    if score is None:
        return redirect(url_for('quiz'))

    return render_template('quiz_result.html',
                           score=score,
                           total=total,
                           percentage=percentage,
                           questions=QUESTIONS,
                           user_answers=user_answers)


@app.route('/report')
def report():
    """
    Awareness report page.
    Shows quiz history, simulation clicks, and a computed awareness level.
    """
    conn = get_db()

    # Fetch the most recent quiz result (if any)
    latest_quiz = conn.execute(
        'SELECT * FROM quiz_results ORDER BY created_at DESC LIMIT 1'
    ).fetchone()

    total_attempts = conn.execute('SELECT COUNT(*) FROM quiz_results').fetchone()[0]
    total_sim_clicks = conn.execute(
        "SELECT COUNT(*) FROM simulation_events WHERE action = 'clicked_link'"
    ).fetchone()[0]
    conn.close()

    # Compute awareness level based on latest quiz score
    level = 'Beginner'
    recommendations = []
    percentage = latest_quiz['percentage'] if latest_quiz else 0

    if percentage >= 80:
        level = 'Good'
        recommendations = [
            'Great work! Keep your knowledge up to date.',
            'Share what you know with colleagues and friends.',
            'Enable multi-factor authentication on all important accounts.',
        ]
    elif percentage >= 50:
        level = 'Intermediate'
        recommendations = [
            'Review the Learn section to strengthen weaker areas.',
            'Practise identifying suspicious email domains.',
            'Always hover over links before clicking to see the real URL.',
        ]
    else:
        level = 'Beginner'
        recommendations = [
            'Start with the Learn section – it covers all key phishing tactics.',
            'Retake the quiz after reading to improve your score.',
            'Remember: legitimate organisations never ask for passwords by email.',
            'When in doubt, contact the company directly via their official website.',
        ]

    return render_template('report.html',
                           latest_quiz=latest_quiz,
                           total_attempts=total_attempts,
                           total_sim_clicks=total_sim_clicks,
                           level=level,
                           recommendations=recommendations)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Initialise the database (creates tables if they don't exist) before starting
    init_db()
    print('PhishGuard: database ready.')
    # debug=True auto-reloads on code changes – disable in production
    app.run(debug=True, port=5000)
