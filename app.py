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

# Login API (Redirects based on role)
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    name = data.get("name")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, password, role FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[1], password):  # If passwords match
        session["user"] = name
        session["role"] = user[2]  # Store role in session
        
        if user[2] == "admin":
            return jsonify({"message": "Login successful", "role": "admin", "redirect": "/admin"})
        elif user[2] == "adopter":
            return jsonify({"message": "Login successful", "role": "adopter", "redirect": "/adopt"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# Register API
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    password = data.get("password")
    role = data.get("role", "adopter")  # Default role is "adopter"

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")  # Hash password

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"error": "User already exists"}), 400

    # Insert new user with hashed password
    cursor.execute("INSERT INTO users (name, password, role) VALUES (?, ?, ?)", (name, hashed_password, role))
    conn.commit()
    conn.close()

    return jsonify({"message": "Registration successful!"})

# Admin Page Route
@app.route("/admin")
def admin():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login_page"))
    return render_template("admin.html")

# Adopter Page Route
@app.route("/adopt")
def adopter():
    if "user" not in session or session.get("role") != "adopter":
        return redirect(url_for("login_page"))
    return render_template("adopter.html")  # Create adopt.html for adopters

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

if __name__ == "__main__":
    app.run(debug=True)
