import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyodbc
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "assets/image"  # Updated path
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__, static_folder="assets", template_folder="templates")
app.secret_key = "your_secret_key"
bcrypt = Bcrypt(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Route to add pet
@app.route("/add_pet", methods=["POST"])
def add_pet():
    if "user" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    name = request.form.get("name")
    age = request.form.get("age")
    sex = request.form.get("sex")
    shelter = request.form.get("shelter")
    image = request.files.get("image")

    if not name or not age or not sex or not shelter:
        return jsonify({"error": "Missing required fields"}), 400

    image_filename = None
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        image.save(image_path)  # Save file

    # Insert into database (Modify query based on your schema)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PETS (PET_NAME, AGE, SEX, SHELTER, IMAGE) VALUES (?, ?, ?, ?, ?)", 
                   (name, age, sex, shelter, image_filename))
    conn.commit()
    conn.close()

    return jsonify({"message": "Pet added successfully!"})

# Route to fetch pets
@app.route("/pets")
def get_pets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, PET_NAME, AGE, SEX, SHELTER, IMAGE, STATUS FROM PETS")
    pets = [{
        "id": row.ID,
        "name": row.PET_NAME,
        "age": row.AGE,
        "sex": row.SEX,
        "shelter": row.SHELTER,
        "image": f"/assets/image/{row.IMAGE}" if row.IMAGE else None,
        "status": row.STATUS
    } for row in cursor.fetchall()]
    conn.close()

    return jsonify(pets)

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
