from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyodbc
from flask_bcrypt import Bcrypt

app = Flask(__name__, static_folder="assets", template_folder="templates")
app.secret_key = "your_secret_key"
bcrypt = Bcrypt(app)

# Database Connection
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=WARLUT-VIRTILAR\\SQLEXPRESS04;"
        "DATABASE=FUREVERFAMILY;"
        "Trusted_Connection=yes;"
    )
    return conn

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Login Page Route
@app.route("/loginAdmin")
def login_page():
    return render_template("loginAdmin.html")

# Login API
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    name = data.get("name")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PASSWORD FROM USERS WHERE NAME = ?", (name,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[0], password):
        session["user"] = name  # Store in session
        return jsonify({"message": "Login successful", "redirect": "/admin"})
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# Register API
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    password = data.get("password")
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM USERS WHERE NAME = ?", (name,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return jsonify({"error": "Username already exists"}), 400

    # Insert new user
    cursor.execute("INSERT INTO USERS (NAME, PASSWORD) VALUES (?, ?)", (name, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({"message": "Registration successful!"})

# Admin Page Route (Protected)
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("admin.html")

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

if __name__ == "__main__":
    app.run(debug=True)
