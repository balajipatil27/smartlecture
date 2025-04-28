from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from transformers import pipeline
from werkzeug.security import generate_password_hash, check_password_hash
import os 
import openai

app = Flask(__name__)
app.secret_key = "supersecretkey"

# openai.api_key = "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"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///users.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Flask-Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# HuggingFace Summarizer Pipeline
summarizer = pipeline("summarization")

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize")
@login_required
def summarize():
    return render_template("summarize.html")

@app.route("/summarize-json", methods=["POST"])
@login_required
def summarize_json():
    data = request.get_json()
    text = data.get('lecture', '')

    if not text or len(text.split()) < 30:
        return jsonify({"error": "Lecture text is too short. Please provide more detailed input."}), 400

    try:
        # Split text into chunks that are less than 1024 tokens (approx 950 words per chunk)
        max_words = 750
        words = text.split()
        
        # Split the text into chunks
        chunks = [words[i:i + max_words] for i in range(0, len(words), max_words)]

        # Summarize each chunk
        summaries = []
        for chunk in chunks:
            chunk_text = ' '.join(chunk)
            summary = summarizer(chunk_text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
            summaries.append(summary)

        # Combine all summaries into one final summary
        final_summary = ' '.join(summaries)

        # Generate questions from the summary
        qas = [{"question": f"What is meant by: {s.strip()}?", "answer": s.strip()} for s in final_summary.split('.') if s.strip()]
        
        return jsonify({"summary": final_summary, "qas": qas})

    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("summarize"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(username=request.form["username"]).first():
            return "Username already exists"
        hashed_password = generate_password_hash(request.form["password"])
        user = User(username=request.form["username"], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# Set OpenAI API key
openai.api_key = os.getenv("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")  # OR directly use your key here (not recommended)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('user_message')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for lecture summarization and learning."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "Error contacting the AI model."})

# MAIN
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database and tables exist
    app.run(debug=True)
