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

@app.route("/adoption_history_data", methods=["GET"])
def adoption_history_data():
    if "user" not in session or session.get("role") != "adopter":
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_user_id(session["user"])  # Get the logged-in user's ID
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all adoption records for the user
        cursor.execute("""
            SELECT 
                p.PET_ID, 
                p.PET_BREED, 
                p.PET_TYPE, 
                p.PHOTO_URL, 
                eva.EVALUATION_STATUS, 
                a.PICKUP_DATE
            FROM ADOPTION a
            JOIN PET p ON a.PET_ID = p.PET_ID
            JOIN EVALUATION eva ON a.ADOPTION_ID = eva.ADOPTION_ID
            WHERE a.[USER_ID] = ?
        """, (user_id,))

        # Map the results to a dictionary
        adoption_history = [{
            "pet_id": row.PET_ID,
            "pet_breed": row.PET_BREED,
            "pet_type": row.PET_TYPE,
            "photo_url": f"/assets/image/{row.PHOTO_URL}" if row.PHOTO_URL else "/assets/default-pet.jpg",
            "status": row.EVALUATION_STATUS,
            "pickup_date": row.PICKUP_DATE or "TBD"
        } for row in cursor.fetchall()]

        conn.close()
        return jsonify(adoption_history), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    

@app.route("/submit_review", methods=["POST"])
def submit_review():
    if "user" not in session or session.get("role") != "adopter":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    shelter_id = data.get("shelter_id")
    review_text = data.get("review")
    rating = data.get("rating")
    user_id = get_user_id(session["user"])

    if not all([shelter_id, review_text, rating]):
        return jsonify({"error": "Missing required fields"}), 400

    if not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO REVIEW (SHELTER_ID, [USER_ID], REVIEW, RATING)
            VALUES (?, ?, ?, ?)
        """, (shelter_id, user_id, review_text, rating))

        conn.commit()
        conn.close()

        return jsonify({"message": "Review submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@app.route("/get_reviews/<int:shelter_id>", methods=["GET"])
def get_reviews(shelter_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.REVIEW_ID, r.REVIEW, r.RATING, u.FIRSTNAME, u.LASTNAME
            FROM REVIEW r
            JOIN [USER] u ON r.[USER_ID] = u.[USER_ID]
            WHERE r.SHELTER_ID = ?
        """, (shelter_id,))

        reviews = [{
            "review_id": row.REVIEW_ID,
            "review": row.REVIEW,
            "rating": row.RATING,
            "user_name": f"{row.FIRSTNAME} {row.LASTNAME}"
        } for row in cursor.fetchall()]

        conn.close()
        return jsonify(reviews), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

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
    

@app.route("/edit_pet/<int:pet_id>", methods=["POST"])
def edit_pet(pet_id):
    if "user" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    # Get form data
    pet_type = request.form.get("pet_type")
    pet_breed = request.form.get("pet_breed")
    pet_weight = request.form.get("pet_weight")
    pet_height = request.form.get("pet_height")
    quantity = request.form.get("quantity")
    image = request.files.get("image")

    if not all([pet_type, pet_breed, pet_weight, pet_height, quantity]):
        return jsonify({"error": "Missing required fields"}), 400

    image_filename = None
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        image.save(image_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if image_filename:
            query = """
                UPDATE PET
                SET PET_TYPE = ?, PET_BREED = ?, PET_WEIGHT = ?, PET_HEIGHT = ?, QUANTITY = ?, PHOTO_URL = ?
                WHERE PET_ID = ?
            """
            params = (pet_type, pet_breed, pet_weight, pet_height, quantity, image_filename, pet_id)
        else:
            query = """
                UPDATE PET
                SET PET_TYPE = ?, PET_BREED = ?, PET_WEIGHT = ?, PET_HEIGHT = ?, QUANTITY = ?
                WHERE PET_ID = ?
            """
            params = (pet_type, pet_breed, pet_weight, pet_height, quantity, pet_id)

        cursor.execute(query, params)
        conn.commit()
        conn.close()

        return jsonify({"message": "Pet updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@app.route("/get_shelters", methods=["GET"])
def get_shelters():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Include IMAGE_URL in the SELECT
        cursor.execute("""
            SELECT SHELTER_ID, SHELTER_NAME, [ADDRESS], CONTACT_NUMBER, EMAIL, IMAGE_URL
            FROM PET_SHELTER
        """)

        shelters = [{
            "shelter_id": row.SHELTER_ID,
            "shelter_name": row.SHELTER_NAME,
            "address": row.ADDRESS,
            "contact_number": row.CONTACT_NUMBER,
            "email": row.EMAIL,
            "image_url": f"/assets/image/{row.IMAGE_URL}" if row.IMAGE_URL else None
        } for row in cursor.fetchall()]

        conn.close()
        return jsonify(shelters), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/add_shelter", methods=["POST"])
def add_shelter():
    if "user" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    # Use form data to support image upload
    shelter_name = request.form.get("shelter_name")
    address = request.form.get("address")
    contact_number = request.form.get("contact_number")
    email = request.form.get("email")
    image = request.files.get("image")

    if not all([shelter_name, address, contact_number, email]):
        return jsonify({"error": "Missing required fields"}), 400

    image_filename = None
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        image.save(image_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO PET_SHELTER (SHELTER_NAME, [ADDRESS], CONTACT_NUMBER, EMAIL, IMAGE_URL)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (shelter_name, address, contact_number, email, image_filename))
        conn.commit()
        conn.close()

        return jsonify({"message": "Shelter added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    

@app.route('/edit_shelter/<int:shelterId>', methods=['PUT'])
def edit_shelter(shelterId):
    try:
        # Get the data from the request

        # Extract the shelter details from the request data
        shelter_name = request.form.get("shelter_name")
        address = request.form.get("address")
        contact_number = request.form.get("contact_number")
        email = request.form.get("email")
        image = request.files.get("image")

        # Check if all required fields are provided
        if not shelter_name or not address or not contact_number or not email:
            return jsonify({'error': 'Missing required fields'}), 400

        # Handle the image if present
        image_filename = None
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image.save(image_path)

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update query with optional image
        if image_filename:
            query = """
            UPDATE PET_SHELTER
            SET SHELTER_NAME = ?, ADDRESS = ?, CONTACT_NUMBER = ?, EMAIL = ?, IMAGE_URL = ?
            WHERE SHELTER_ID = ?
            """
            params = (shelter_name, address, contact_number, email, image_filename, shelterId)
        else:
            query = """
            UPDATE PET_SHELTER
            SET SHELTER_NAME = ?, ADDRESS = ?, CONTACT_NUMBER = ?, EMAIL = ?
            WHERE SHELTER_ID = ?
            """
            params = (shelter_name, address, contact_number, email, shelterId)

        # Execute the update query
        cursor.execute(query, params)
        
        # Commit the changes to the database
        conn.commit()

        # Check if any rows were affected (to ensure the update was successful)
        if cursor.rowcount > 0:
            return jsonify({'message': 'Shelter updated successfully'}), 200
        else:
            return jsonify({'error': 'Shelter not found'}), 404

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Could not update shelter data'}), 500



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

@app.route('/get_shelter/<int:shelterId>', methods=['GET'])
def get_shelter(shelterId):
    print(f"Fetching Shelter with ID: {shelterId}")  # Debugging line
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM PET_SHELTER WHERE SHELTER_ID = ?", (shelterId,))
        row = cursor.fetchone()

        if row:
            return jsonify({
                'shelter_id': row.SHELTER_ID,
                'address': row.ADDRESS,
                'shelter_name': row.SHELTER_NAME,
                'contact_number': row.CONTACT_NUMBER,
                'email': row.EMAIL,
                'image_url': f"/assets/image/{row.IMAGE_URL}" if row.IMAGE_URL else None
            }), 200
        else:
            return jsonify({'error': 'SHELTER not found'}), 404

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Could not load SHELTER data'}), 500



@app.route('/get_pet/<int:petId>', methods=['GET'])
def get_pet(petId):
    print(f"Fetching pet with ID: {petId}")  # Debugging line
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM PET WHERE PET_ID = ?", (petId,))
        row = cursor.fetchone()

        if row:
            return jsonify({
                'pet_id': row.PET_ID,
                'pet_type': row.PET_TYPE,
                'pet_breed': row.PET_BREED,
                'pet_weight': row.PET_WEIGHT,
                'pet_height': row.PET_HEIGHT,
                'quantity': row.QUANTITY,
                'photo_url': row.PHOTO_URL
            }), 200
        else:
            return jsonify({'error': 'Pet not found'}), 404

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Could not load pet data'}), 500




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

        # Pass image_filename as both @PhotoURL and @Image_url
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
                @Email = ?, 
                @Image_url = ?
        """, (
            user_id, pet_type, pet_breed, image_filename, pet_weight, pet_height,
            quantity, shelter_address, shelter_name, contact_number, email, image_filename
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

        pets = []
        for row in cursor.fetchall():
            pets.append({
                "pet_id": row.PET_ID,
                "user_id": row.USER_ID,
                "pet_type": row.PET_TYPE,
                "pet_breed": row.PET_BREED,
                "photo_url": f"/assets/image/{row.PHOTO_URL}" if row.PHOTO_URL else "/assets/default-pet.jpg",
                "pet_weight": float(row.PET_WEIGHT) if row.PET_WEIGHT is not None else None,
                "pet_height": float(row.PET_HEIGHT) if row.PET_HEIGHT is not None else None,
                "quantity": row.QUANTITY,
                "shelter_id": row.SHELTER_ID,
                "shelter_name": row.SHELTER_NAME,
                "shelter_address": row.SHELTER_ADDRESS,
                "contact_number": row.CONTACT_NUMBER,
                "email": row.EMAIL
            })

        cursor.close()
        conn.close()
        return jsonify(pets)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route to apply for adoption
@app.route("/application", methods=["POST"])
def application():
    if "user" not in session or session.get("role") != "adopter":
        return jsonify({"error": "Unauthorized"}), 403

    # Get adopter's information from the request
    data = request.json
    print("Received application data:", data)  # Debugging

    pet_id = data.get("pet_id")
    no_adoption = data.get("no_adoption")
    pickup_date = data.get("pickup_date")
    adoption_income = data.get("adoption_income")
    adoption_history = data.get("adoption_history")
    behavioral_assess = data.get("behavioral_assess")

    # Validate required fields
    if not all([pet_id, no_adoption, pickup_date, adoption_income, adoption_history, behavioral_assess]):
        return jsonify({"error": "Missing required fields"}), 400

    # Get adopter's user_id
    user_id = get_user_id(session["user"])
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute stored procedure for adoption application
        cursor.execute("""
            EXEC sp_ApplyForAdoptionWithDetails 
                @PET_ID = ?, 
                @USER_ID = ?, 
                @NO_ADOPTION = ?, 
                @PICKUP_DATE = ?, 
                @ADOPTION_INCOME = ?, 
                @ADOPTION_HISTORY = ?, 
                @BEHAVIORAL_ASSESS = ?
        """, (
            pet_id, user_id, no_adoption, pickup_date, adoption_income, 
            adoption_history, behavioral_assess
        ))

        # Commit and close connection
        conn.commit()
        conn.close()

        return jsonify({"message": "Adoption application submitted successfully!"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route to get adoption applications with pet photo and application form
@app.route("/get_adoption_applications", methods=["GET"])
def get_adoption_applications():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the stored procedure
        cursor.execute("EXEC sp_GetAdoptionApplications")

        # Fetch the results and map them to a dictionary
        applications = [{
            "evaluation_id": row.EVALUATION_ID,
            "evaluation_status": row.EVALUATION_STATUS,
            "adoption_income": row.ADOPTION_INCOME,
            "adoption_history": row.ADOPTION_HISTORY,
            "behavioral_assess": row.BEHAVIORAL_ASSESS,
            "evaluation_date": row.EVALUATION_DATE,

            "adoption_id": row.ADOPTION_ID,
            "no_adoption": row.NO_ADOPTION,
            "pickup_date": row.PICKUP_DATE,
            "adoption_date": row.ADOPTION_DATE,

            "pet_id": row.PET_ID,
            "pet_breed": row.PET_BREED,
            "photo_url": f"/assets/image/{row.PHOTO_URL}" if row.PHOTO_URL else None,

            "shelter_name": row.SHELTER_NAME,
            "shelter_address": row.SHELTER_ADDRESS,

            "adopter_firstname": row.FIRSTNAME,
            "adopter_lastname": row.LASTNAME,

            "user_id": row.USER_ID
        } for row in cursor.fetchall()]

        conn.close()
        return jsonify(applications), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 500

@app.route("/approve_application/<int:evaluation_id>", methods=["POST"])
def approve_application(evaluation_id):
    if "user" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the stored procedure to approve the application
        cursor.execute("EXEC sp_ApproveAdoptionApplication @EvaluationID = ?", (evaluation_id,))
        
        conn.commit()
        conn.close()

        return jsonify({"message": "Application approved successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
    
    
@app.route("/reject_application/<int:evaluation_id>", methods=["POST"])
def reject_application(evaluation_id):
    if "user" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the stored procedure to approve the application
        cursor.execute("EXEC sp_RejectAdoptionApplication @EvaluationID = ?", (evaluation_id,))
        
        conn.commit()
        conn.close()

        return jsonify({"message": "Rejected!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

'''@app.route('/adoption_history_page')
def adoption_history_page():
    user_id = get_user_id(session["user"])  # Function to get USER_ID from username
    if not user_id:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.PET_ID, p.PET_BREED, p.PET_TYPE, p.PHOTO_URL,
            eva.EVALUATION_STATUS, a.PICKUP_DATE
        FROM ADOPTION a
        JOIN PET p ON a.PET_ID = p.PET_ID
        JOIN [USER] u ON a.[USER_ID] = u.[USER_ID]
        JOIN EVALUATION eva ON a.ADOPTION_ID = eva.ADOPTION_ID
        WHERE a.ADOPTER_ID = ?
    """, user_id)

    rows = cursor.fetchall()
    adoption_history = [{
        "pet_id": row.PET_ID,
        "pet_breed": row.PET_BREED,
        "pet_type": row.PET_TYPE,
        "photo_url": row.PHOTO_URL,
        "status": row.EVALUATION_STATUS,
        "pickup_date": row.PICKUP_DATE
    } for row in rows]

    return jsonify(adoption_history)
'''


# Admin Page Route
@app.route("/admin")
def admin():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login_page"))
    return render_template("admin.html")


@app.route("/adoption_history")
def adoption_history():
    if "user" not in session or session.get("role") != "adopter":
        return redirect(url_for("login_page"))
    return render_template("adoption_history.html")



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