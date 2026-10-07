# PhishGuard – Phishing Awareness Training Platform

A beginner-friendly, educational web application that teaches users how to recognise and avoid phishing attacks. Built with Python Flask and SQLite — no external APIs or authentication services required.

---

## Project Objective

Phishing is one of the most common and effective cyber attacks today. This platform provides an interactive, hands-on way to:

- **Learn** the techniques attackers use
- **Experience** a safe, realistic phishing simulation
- **Test** knowledge with a scenario-based quiz
- **Track** personal awareness progress

---

## Technologies Used

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3 · Flask                  |
| Database   | SQLite (via Python's built-in `sqlite3`) |
| Frontend   | HTML5 · CSS3 (custom) · Vanilla JavaScript |
| Templates  | Jinja2 (Flask's built-in engine)  |

No Node.js, React, Docker, external APIs, email services, or third-party authentication.

---

## Features

1. **Dashboard** – Overview of the platform with live statistics (quiz attempts, simulation clicks, average score).
2. **Learn** – Eight topic guide covering phishing types, URL tricks, urgency tactics, fake login pages, sender checking, attachments, and safety best practices.
3. **Safe Phishing Simulation** – A realistic-looking fake phishing email. Clicking the link records an anonymous event and takes the user to a training explanation page. **No credentials are collected.**
4. **Quiz** – Five multiple-choice scenario questions. Scores are saved to SQLite and reviewed with explanations.
5. **Awareness Report** – Shows latest quiz score, simulation history, awareness level (Beginner / Intermediate / Good), and personalised recommendations.

---

## Project Structure

```
phishing-awareness-platform/
├── app.py              ← Flask application and routes
├── requirements.txt    ← Python dependencies
├── database.db         ← SQLite database (auto-created on first run)
├── README.md
├── templates/
│   ├── base.html       ← Shared layout (navbar, footer)
│   ├── index.html      ← Dashboard
│   ├── learn.html      ← Educational content
│   ├── simulation.html ← Fake phishing email
│   ├── result.html     ← Post-simulation training page
│   ├── quiz.html       ← Quiz form
│   ├── quiz_result.html← Score + answer review
│   └── report.html     ← Awareness report
└── static/
    ├── style.css       ← Cybersecurity-themed dark UI
    └── script.js       ← Minimal vanilla JS
```

---

## How to Install

**Prerequisites:** Python 3.8 or higher

```bash
# 1. Clone or download this repository
cd phishing-awareness-platform

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## How to Run

```bash
python app.py
```

The terminal will show:
```
PhishGuard: database ready.
 * Running on http://127.0.0.1:5000
```

Open your browser and visit: **http://127.0.0.1:5000**

The SQLite database (`database.db`) is created automatically on the first run.

---

## Routes

| URL                   | Page                          |
|-----------------------|-------------------------------|
| `/`                   | Dashboard                     |
| `/learn`              | Educational guide             |
| `/simulation`         | Phishing simulation email     |
| `/simulation-click`   | Records click, redirects      |
| `/result`             | Training explanation          |
| `/quiz`               | Quiz (GET = form, POST = submit) |
| `/quiz-result`        | Score and answer review       |
| `/report`             | Awareness report              |

---

## How the Safe Phishing Simulation Works

1. The user visits `/simulation` and sees a realistic-looking fake phishing email.
2. The email contains a button labelled **"Verify My Account Now"**.
3. If the user clicks it, the browser is sent to `/simulation-click`.
4. The server writes a single anonymous record (`action = 'clicked_link'`) to the `simulation_events` table — **nothing else**.
5. The user is immediately redirected to `/result`, which explains exactly what made the email suspicious and what to do in a real situation.
6. If the user skips the button, they can go directly to `/result` to see the explanation anyway.

**At no point is any password, email address, personal name, or identifying information requested or stored.**

---

## Security & Privacy Note

- **No real credentials are collected.** The simulation does not have a fake login page.
- **No personal data is stored.** The database only records anonymous counts (quiz scores, click events).
- **No external network calls are made.** The application runs entirely on your local machine.
- **The secret key** in `app.py` is a development placeholder. For any production deployment, load it from an environment variable.
- This platform is designed purely for educational purposes. It should not be used to test employees without their knowledge or consent.

---

## Awareness Levels

| Score Range | Level        |
|-------------|--------------|
| 80 – 100 %  | Good         |
| 50 – 79 %   | Intermediate |
| 0 – 49 %    | Beginner     |

Levels are calculated from the most recent quiz attempt.
