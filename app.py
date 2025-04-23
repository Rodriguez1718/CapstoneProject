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
        "SERVER=CCSLAB530U46;"
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
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400

        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user exists
        cursor.execute("SELECT PASSWORD, ROLE FROM [USER] WHERE USERNAME = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and bcrypt.check_password_hash(row[0], password):  # Check password hash
            return jsonify({"message": "Login successful!", "role": row[1]})
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Register API
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    phone = data.get("phone")
    address = data.get("address")
    role = data.get("role", "adopter")  # Default role is "adopter"
    username = data.get("username")
    password = data.get("password")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")  # Hash password

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists (by username)
    cursor.execute("SELECT * FROM [USER] WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return jsonify({"error": "User already exists"}), 400

    # Call the stored procedure to register the user
    cursor.execute("""
        EXEC RegisterUser
            @FIRSTNAME = ?, 
            @LASTNAME = ?, 
            @PHONE = ?, 
            @ADDRESS = ?, 
            @ROLE = ?, 
            @USERNAME = ?, 
            @PASSWORD = ?
    """, (firstname, lastname, phone, address, role, username, hashed_password))

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
@app.route("/adopter")
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
