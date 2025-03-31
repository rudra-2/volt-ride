from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
from datetime import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# MySQL Database Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="voltride"
)
cursor = db.cursor(dictionary=True)

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
otp_storage = {}
# Generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via Email using App Password
def send_otp_via_email(email, otp, name):
    try:
        sender_email = "voltride.infinite@gmail.com"
        app_password = "dvgn utdq phba edmv"  # Use the generated app password
        subject = "Volt Ride OTP"
             # HTML message body with OTP styled in bold and custom color
        # HTML message body with OTP styled in bold and custom color
        message_body = f"""
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                    }}
                    .otp {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #000000;
                    }}
                    .content {{
                        word-wrap: break-word;
                        white-space: normal;
                    }}
                </style>
            </head>
            <body>
                <p>Hello {name},</p>

                <p>Your OTP (One-Time Password) for Volt Ride is: <span class="otp">{otp}</span>. This code is required to complete your authentication process.</p>

                <p class="content">If you did not request this OTP, please disregard this email.</p>

                <p class="content">Thank you for choosing Volt Ride!</p>

                <p class="content">Regards,<br>Volt Ride Team</p>
            </body>
            </html>
        """


        # Create Email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'html'))

        # Send Email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email, msg.as_string())
        
        print(f"OTP {otp} sent to {email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP: {e}")
        return False

@app.route("/")
def home():
    return render_template("index.html")

# ------------------ AUTH ROUTES ------------------

# Send OTP Endpoint
@app.route('/send_otp', methods=['POST'])
def send_otp():
    name = request.form.get('signUpName')
    email = request.form.get('signUpNum')
    print(email)

    otp = generate_otp()
    otp_storage[email] = otp

    if send_otp_via_email(email, otp, name):
        return render_template('otp_input.html', email=email)
    else:
        return render_template('error.html', message="Failed to send OTP")
    
    
# OTP Input Page
@app.route('/otp_input/<email>', methods=['GET', 'POST'])
def otp_input(email):
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if otp_storage.get(email) == entered_otp:
            return render_template('register.html', email=email)
            # return render_template('success.html', message="OTP verified successfully!")
        else:
            return render_template('error.html', message="Incorrect OTP, please try again.")

    return render_template('otp_input.html', email=email)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cursor.execute("SELECT email, password FROM user WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and user["password"] == password:
            session["user_email"] = user["email"]
            return redirect(url_for("dashboard"))
        else:
            print(email, password)
            return jsonify({"error": "Invalid email or password"}), 401

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form

        # Debugging: Print received form data
        print("Received Data:", data)

        # Check if all fields exist
        required_fields = ["firstName", "lastName", "email", "mobile", "password", "licencePhotoURL", "licenceNumber"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return redirect(url_for("register"))

        try:
            cursor.execute("""
                INSERT INTO user (`first-name`, `last-name`, email, mobile, password, `licence-photo`, `licence-number`, approval)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """, (data["firstName"], data["lastName"], data["email"], data["mobile"], 
                  data["password"], data["licencePhotoURL"], data["licenceNumber"]))
            
            db.commit()
            session["user_email"] = data["email"]
            return redirect(url_for("login"))
        
        except mysql.connector.Error as err:
            print("MySQL Error:", err)  # Log MySQL errors
            return jsonify({"error": f"MySQL Error: {err}"}), 400
        
        except Exception as e:
            print("General Error:", e)
            return jsonify({"error": str(e)}), 400

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("login"))

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json  # Expecting JSON data
    email = data.get("email")
    password = data.get("password")

    # Fetch admin details from MySQL
    cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
    admin = cursor.fetchone()

    if admin and admin["password"] == password:  # Validate password without hashing
        session["admin_id"] = admin["id"]  # Store admin session
        return jsonify({"message": "Admin login successful", "admin_id": admin["id"]}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)  # Remove admin session
    return jsonify({"message": "Admin logged out"}), 200



@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")


# ------------------ VEHICLE ROUTES ------------------

@app.route('/vehicles', methods=["GET", "POST"])
def vehicles():
    if request.method == "POST":
        data = request.json
        cursor.execute("INSERT INTO vehicle (reg-plate, name, battery, station-id) VALUES (%s, %s, %s, %s)",
                       (data["reg_plate"], data["name"], data["battery"], data["station_id"]))
        db.commit()
        return jsonify({"message": "Vehicle added successfully!"}), 201

    cursor.execute("SELECT * FROM vehicle")
    vehicles = cursor.fetchall()
    return jsonify(vehicles)


@app.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    cursor.execute("SELECT * FROM vehicle WHERE v-id = %s", (vehicle_id,))
    vehicle = cursor.fetchone()
    if vehicle:
        return jsonify(vehicle)
    return jsonify({"error": "Vehicle not found"}), 404


# ------------------ RIDE ROUTES ------------------

@app.route("/ride/start", methods=["POST"])
def start_ride():
    data = request.json
    cursor.execute("INSERT INTO ride (user-id, v-id, time, date, status) VALUES (%s, %s, NOW(), CURDATE(), 'ongoing')",
                   (data["userId"], data["vehicleId"]))
    db.commit()
    return jsonify({"message": "Ride started"})


@app.route("/ride/end/<int:ride_id>", methods=["POST"])
def end_ride(ride_id):
    cursor.execute("SELECT user-id, v-id FROM ride WHERE r-id = %s AND status = 'ongoing'", (ride_id,))
    ride = cursor.fetchone()

    if ride:
        fare = calculate_fare(ride_id)
        cursor.execute("SELECT amount FROM wallet WHERE user-id = %s", (ride["user-id"],))
        wallet = cursor.fetchone()

        if wallet and wallet["amount"] >= fare:
            cursor.execute("UPDATE wallet SET amount = amount - %s WHERE user-id = %s", (fare, ride["user-id"]))
            cursor.execute("UPDATE ride SET status='completed' WHERE r-id = %s", (ride_id,))
            db.commit()
            return jsonify({"message": "Ride ended", "fare": fare})
        return jsonify({"error": "Insufficient balance"}), 400

    return jsonify({"error": "Ride not found"}), 404


# ------------------ WALLET & PAYMENTS ------------------

@app.route("/wallet", methods=["GET", "POST"])
def wallet():
    if request.method == "POST":
        data = request.json
        cursor.execute("UPDATE wallet SET amount = amount + %s WHERE user-id = %s", (data["amount"], data["userId"]))
        cursor.execute("INSERT INTO transaction (user-id, method, amount) VALUES (%s, %s, %s)",
                       (data["userId"], data["method"], data["amount"]))
        db.commit()
        return jsonify({"message": "Wallet recharged"})

    cursor.execute("SELECT * FROM wallet WHERE user-id = %s", (session.get("user_email"),))
    wallet = cursor.fetchone()
    return jsonify(wallet)


# ------------------ HELPER FUNCTIONS ------------------

def calculate_fare(ride_id):
    """Calculate ride fare based on fixed distance"""
    total_distance = 5  # Replace with actual distance calculation
    fare = 10 + (total_distance * 2)
    return max(fare, 20)


# ------------------ RUN SERVER ------------------

if __name__ == '__main__':
    app.run(debug=True)