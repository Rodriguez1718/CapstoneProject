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
        "SERVER=LAPTOP-DHGH0RSF\SQLEXPRESS;"
        "DATABASE=FUREVERFAMILY;"
        "Trusted_Connection=yes;"   
    )
    return conn

def get_user_id(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT USER_ID FROM [USER] WHERE USERNAME = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row.USER_ID if row else None


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

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT PASSWORD, ROLE FROM [USER] WHERE LOWER(USERNAME) = LOWER(?)", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and bcrypt.check_password_hash(row[0], password):
            session['user'] = username  # <-- ADD THIS
            session['role'] = row[1]    # <-- ADD THIS
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

    # Pet info
    pet_type = request.form.get("pet_type")
    pet_breed = request.form.get("pet_breed")
    pet_weight = request.form.get("pet_weight")
    pet_height = request.form.get("pet_height")
    quantity = request.form.get("quantity")
    
    # Shelter info
    shelter_address = request.form.get("shelter_address")
    shelter_name = request.form.get("shelter_name")
    contact_number = request.form.get("contact_number")
    email = request.form.get("email")

    # Image
    image = request.files.get("image")

    if not all([pet_type, pet_breed, pet_weight, pet_height, quantity, 
                shelter_address, shelter_name, contact_number, email]):
        return jsonify({"error": "Missing required fields"}), 400

    # Save image
    image_filename = None
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        image.save(image_path)
    else:
        return jsonify({"error": "Invalid or missing image file"}), 400

    user_id = get_user_id(session["user"])  # Function to get USER_ID from username

    if user_id is None:
        return jsonify({"error": "User not found"}), 404

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            EXEC sp_AddPetWithShelter 
                @UserID = ?, 
                @PetType = ?, 
                @PetBreed = ?, 
                @PhotoURL = ?, 
                @PetWeight = ?, 
                @PetHeight = ?, 
                @Quantity = ?, 
                @ShelterAddress = ?, 
                @ShelterName = ?, 
                @ContactNumber = ?, 
                @Email = ?
        """, (
            user_id, pet_type, pet_breed, image_filename, pet_weight, pet_height,
            quantity, shelter_address, shelter_name, contact_number, email
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "Pet and shelter saved successfully!"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route to fetch pets with shelter info
@app.route("/get_pets")
def get_pets():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the stored procedure
        cursor.execute("EXEC sp_GetPetsWithShelter")

        pets = [{
            "pet_id": row.PET_ID,
            "user_id": row.USER_ID,
            "pet_type": row.PET_TYPE,
            "pet_breed": row.PET_BREED,
            "photo_url": f"/assets/image/{row.PHOTO_URL}" if row.PHOTO_URL else None,
            "pet_weight": float(row.PET_WEIGHT),
            "pet_height": float(row.PET_HEIGHT),
            "quantity": row.QUANTITY,
            "shelter_id": row.SHELTER_ID,
            "shelter_name": row.SHELTER_NAME,
            "shelter_address": row.SHELTER_ADDRESS,
            "contact_number": row.CONTACT_NUMBER,
            "email": row.EMAIL
        } for row in cursor.fetchall()]

        conn.close()
        return jsonify(pets)
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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
    return render_template("adopter.html")

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

if __name__ == "__main__":
    app.run(debug=True)