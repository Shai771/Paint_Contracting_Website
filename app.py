from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests 
from db_model import db, ContactForm, UserCredentials,PaintMaterials

app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost:3307/trail"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.secret_key = "your_secret_key"


# Initialize database with app
db.init_app(app)


with app.app_context():
    db.metadata.reflect(bind=db.engine)  # Force schema refresh


# Ensure tables are created
with app.app_context():
    db.create_all()


@app.route("/")
@app.route("/homeb")  # Home page before login
def homeb():
    if "user_id" in session:
        return redirect(url_for("home"))  # Redirect logged-in users to home
    return render_template("home_bef_log.html")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         # Fetch user from the database
#         user = UserCredentials.query.filter_by(email=email).first()

#         if user and user.password == password:  # Compare passwords 
#             session["user_id"] = user.user_id  # Store user session
#             flash("Login successful!", "success")
#             return redirect(url_for("home"))  # Redirect to home after login
#         else:
#             flash("Invalid email or password. Please try again.", "danger")

#     return render_template("login.html")

# login page logic
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Fetch user from the database
        user = UserCredentials.query.filter_by(email=email).first()

        if user and user.password == password:
            session["user_id"] = user.user_id
            session["flash_message"] = ("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            session["flash_message"] = ("Invalid email or password. Please try again.", "danger")
            return redirect(url_for("login"))

    # Show flash message if it exists
    if "flash_message" in session:
        message, category = session.pop("flash_message")  # Show once
        flash(message, category)

    return render_template("login.html")

  

@app.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove user from session
    flash("You have been logged out.", "info")
    return redirect(url_for("homeb"))  # Redirect to homeb after logout

@app.route("/home")  # Home page after login
def home():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("homeb"))  # Redirect unauthorized users to homeb
    return render_template("home.html")

@app.route("/About")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contactUs")
def contactUs():
    return render_template("contactUs.html")

@app.route("/budget")
def budget_cal():
    return render_template("budget_cal.html")


# route to handle the subbsion and calculation of prices 
@app.route("/calculate_price", methods=["POST"])
def calculate_price():
    try:
        # Fetch user inputs
        project_type = request.form.get("project_type")  # Fresh Painting or Re-Painting
        project_space = request.form.get("project_space")  # Interior or Exterior
        square_feet = float(request.form.get("square_feet"))

        # Fetch all paints from the database
        paints = PaintMaterials.query.all()

        # Define multipliers based on user selection+9+
        multipliers = {
            ("Fresh Painting", "Interior"): 1.0,
            ("Fresh Painting", "Exterior"): 1.5,
            ("Re-Painting", "Interior"): 0.8,
            ("Re-Painting", "Exterior"): 1.0
        }

        # Get the correct multiplier based on user selection
        multiplier = multipliers.get((project_type, project_space), 1.0)

        # Calculate price for each paint
        results = []
        for paint in paints:
            total_price = paint.per_cost * square_feet * multiplier  # Use per_cost instead of per_sqrt_price
            results.append({
                "paint_name": paint.paint_name,
                "paint_brand":paint.paint_brand,
                "per_cost": paint.per_cost,
                "total_price": round(total_price, 2)  # Rounding for better display
            })

        session["results"] = results  # Store in session
        print("DEBUG: Stored results in session:", results)  # Debugging

        return redirect(url_for("result"))  # Redirect to result.html
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    



@app.route("/result")
def result():
    return render_template("result.html")  # Load the results page

@app.route("/get_results")
def get_results():
    results = session.get("results", [])
    print("DEBUG: Sending results to result.html:", results)  # Debugging
    return jsonify({"status": "success", "data": results})



@app.route("/guide")
def col_guide():
    return render_template("col_guide.html")

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    pincode = request.form['pincode']
    project_type = request.form['project_type']
    project_space = request.form['project_space']
    square_feet = request.form['square_feet']

    # Create a new ContactForm entry and add it to the database
    new_entry = ContactForm(
        name=name, email=email, mobile=mobile, pincode=pincode,
        project_type=project_type, project_space=project_space, square_feet=square_feet
    )
    db.session.add(new_entry)
    db.session.commit()

    return "Form Submitted Successfully!"  # You can redirect to a success page


# sign in path
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]

        # Check if email already exists
        existing_user = UserCredentials.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already taken. Try another one.", "danger")
            return redirect(url_for("signin"))

        # Validate that both passwords match
        if password != password2:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for("signin"))
        
          # Validate email authenticity using API
        if not verify_email(email):
            flash("Please enter a real and valid email address!", "danger")
            return redirect(url_for("signin"))


        # Store password directly (not encrypted) - Ensure column name matches database
        new_user = UserCredentials(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Sign-up successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signIn.html")


# Function to Check If Email is Real (Using API)
def verify_email(email):
    api_key = "08b500a71310949fdc4c45522638160e"  # Replace this with your new API key
    try:
        response = requests.get(
            f"http://apilayer.net/api/check?access_key={api_key}&email={email}&smtp=1&format=1",
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        print("API Response:", result)  # Debugging

        # Check if the email format is valid and SMTP is working
        return result.get("format_valid") and result.get("smtp_check")

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return False  # Treat failures as invalid email


@app.route('/forgot_password')
def forgot_password():
    return render_template("forgot_password.html")


# Running the app
if __name__ == "__main__":
    app.run(debug=True)
