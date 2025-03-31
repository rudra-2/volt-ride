from flask import Flask, request, jsonify, render_template, redirect, flash, url_for, session
from pymongo import MongoClient, UpdateOne, InsertOne
from pymongo.errors import BulkWriteError, ServerSelectionTimeoutError
from bson.objectid import ObjectId
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import base64
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore, storage
from werkzeug.security import generate_password_hash
import time
from datetime import datetime
import traceback
import cv2
from pyzbar.pyzbar import decode
from geopy.distance import geodesic

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = '1952'

app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# OTP storage
otp_storage = {}

# Check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'your-firebase-app-id.appspot.com',
    })

# MongoDB Configuration
try:
    client = MongoClient(
        "mongodb+srv://mhpatel2026:ASDFGHJKL@cluster0.y2dqwmk.mongodb.net/hk?retryWrites=true&w=majority",
        serverSelectionTimeoutMS=60000,  # 60 seconds timeout
        connectTimeoutMS=60000,          # 60 seconds connection timeout
        socketTimeoutMS=60000,           # 60 seconds socket timeout
        maxPoolSize=50,                  # Maximum number of connections in the pool
        minPoolSize=10,                  # Minimum number of connections in the pool
        retryWrites=True,                # Enable retry of write operations
        retryReads=True,                 # Enable retry of read operations
        ssl=True                         # Enable SSL/TLS
    )
    # Test the connection
    client.admin.command('ping')
    db = client["hk"]
    print("Connected to MongoDB successfully!")
except ServerSelectionTimeoutError as e:
    print(f"Error connecting to MongoDB: {e}")
    print("Please check your internet connection and MongoDB Atlas network access settings.")
    exit(1)
except Exception as e:
    print(f"Unexpected error connecting to MongoDB: {e}")
    print("Please verify your MongoDB connection string and credentials.")
    exit(1)

# Generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via Email
def send_otp_via_email(email, otp, name):
    try:
        sender_email = "voltride.infinite@gmail.com"
        app_password = "dvgn utdq phba edmv"
        subject = "Volt Ride OTP"
        message_body = f"""
            <html>
            <body>
                <p>Hello {name},</p>
                <p>Your OTP for Volt Ride is: <b>{otp}</b>.</p>
                <p>Thank you for choosing Volt Ride!</p>
            </body>
            </html>
        """
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email, msg.as_string())
        
        print(f"OTP {otp} sent to {email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    name = request.form.get('signUpName')
    email = request.form.get('signUpNum')

    otp = generate_otp()
    otp_storage[email] = otp

    if send_otp_via_email(email, otp, name):
        return render_template('otp_input.html', email=email)
    else:
        return render_template('error.html', message="Failed to send OTP")

@app.route('/register/<email>', methods=['GET', 'POST'])
def register(email):
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        mobile = request.form.get('mobile')
        password = request.form.get('passwordHash')
        confirm_password = request.form.get('confirmPassword')
        licence_number = request.form.get('licenceNumber')
        file = request.files.get('licencePhoto')

        if not file or file.filename == '':
            flash("No selected file", 'danger')
            return render_template('register.html', email=email)
        
        if not allowed_file(file.filename):
            flash("Invalid file type. Only images are allowed.", 'danger')
            return render_template('register.html', email=email)

        if password != confirm_password:
            flash("Passwords do not match!", 'danger')
            return render_template('register.html', email=email)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        with open(file_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

        try:
            db.user.insert_one({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "mobile": mobile,
                "password": password,
                "licence_photo": encoded_string,
                "licence_number": licence_number,
                "approval": "pending"
            })
            flash('Registration successful! Please wait for approval.', 'success')
            return redirect(url_for("login"))
        except Exception as e:
            print("Error:", e)
            flash(f"An unexpected error occurred: {e}", 'danger')
            return render_template('register.html', email=email)
    return render_template("register.html", email=email)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        print(email, password)
        user = db.user.find_one({"email": email})
        print(user)
        if user and user["password"] == password:
            session["email_id"] = user["email"]
            print(user["email"],user["password"])
            session["role"] = user["role"]
            session["user_id"] = user["user_id"]
            if user["role"] == 'master':
                return render_template('admin_dashboard.html')
            elif user["role"] == 'user':
                return redirect(url_for('vehicles'))
        else:
            return render_template('error.html', message="Invalid email or password")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session['role'] == 'master':
        print(session['email_id'])
        # Fetch admin details from MongoDB
        user = db.user.find_one({"email": session['email_id']})
        station = db.stations.find_one({"master_id": user["user_id"]})
        session['station-id'] = station['station_id']
        return render_template('admin_dashboard.html')
    elif session['role'] == 'user':
        return redirect(url_for('vehicles'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about_us.html')

@app.route("/logout")
def logout():
    session.pop("email_id", None)
    session.pop("role", None)
    return redirect(url_for("index"))

@app.route('/vehicle', methods=['GET', 'POST'])
def vehicles():
    try:
        if session['role'] == 'master':
            vehicles_data = list(db.vehicle.find())
            return render_template('vehicle_details.html', vehicles=vehicles_data)
        elif session['role'] == 'user':
            stations = list(db.stations.find())
            
            # Fetch all available vehicles
            vehicles_data = list(db.vehicle.find({"status": "Available"}))
            
            # Add station names and IDs to vehicle data
            for vehicle in vehicles_data:
                station = next((s for s in stations if s['station_id'] == vehicle['station_id']), None)
                vehicle['station_name'] = station['name'] if station else 'Unknown Station'
                vehicle['station_id'] = str(vehicle['station_id'])  # Convert to string for comparison
            
            return render_template('user_dashboard.html', vehicles=vehicles_data, stations=stations)
    except Exception as e:
        print("Error:", e)
        flash("Failed to fetch vehicle data", 'danger')
        return render_template('vehicle_details.html', vehicles=[])

@app.route('/vehicle/edit/<vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    try:
        # Fetch vehicle data for pre-filling the form
        vehicle = db.vehicle.find_one({"v_id": vehicle_id})

        if not vehicle:
            flash("Vehicle not found", 'danger')
            return redirect(url_for('vehicles'))

        # Fetch stations for dropdown
        stations = list(db.stations.find())

        if request.method == 'POST':
            reg_plate = request.form['reg_plate']
            name = request.form['name']
            battery = float(request.form['battery'])
            station_id = request.form['station_id']
            status = request.form['status']

            # Update vehicle details
            db.vehicle.update_one(
                {"v_id": (vehicle_id)},
                {"$set": {
                    "reg_plate": reg_plate,
                    "name": name,
                    "battery": battery,
                    "station_id": station_id,
                    "status": status
                }}
            )

            flash("Vehicle updated successfully", "success")
            return redirect(url_for('vehicles'))

        return render_template('edit_vehicle.html', vehicle=vehicle, stations=stations)

    except Exception as e:
        print("Error:", e)
        flash("Failed to edit vehicle", 'danger')
        return redirect(url_for('vehicles'))

@app.route('/vehicle/delete/<vehicle_id>')
def delete_vehicle(vehicle_id):
    try:
        # Check if the vehicle exists
        vehicle = db.vehicle.find_one({"v_id": vehicle_id})
        if not vehicle:
            flash("Vehicle not found", "danger")
            return redirect(url_for('vehicles'))

        # Perform deletion
        db.vehicle.delete_one({"v_id": vehicle_id})
        db.charging_ports.update_many(
            {"vehicle_id": vehicle_id},
            {"$set": {"vehicle_id": "", "battery": ""}}
        )

        flash("Vehicle deleted successfully", "success")
    except Exception as e:
        print("Error:", e)
        flash("Failed to delete vehicle", 'danger')
    return redirect(url_for('vehicles'))

@app.route('/station')
def station_details():
    try:
        # Fetch Station Details
        station = db.stations.find_one({"station_id": session['station-id']})
        
        # Fetch Charging Port Details
        ports = list(db.charging_ports.find({"station_id": session['station-id']}))
        
        # Add vehicle details to ports
        for port in ports:
            if port.get('vehicle_id'):
                vehicle = db.vehicle.find_one({"v_id": port['vehicle_id']})
                if vehicle:
                    port['battery'] = vehicle.get('battery', '-')
                else:
                    port['battery'] = '-'
            else:
                port['battery'] = '-'

        return render_template('station_details.html', station=station, ports=ports)
    except Exception as e:
        print("Error:", e)
        flash("Failed to fetch station details", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/profile')
def profile():
    try:
        email = session['email_id']
        # Get User Details
        user = db.user.find_one({"email": email})

        if not user:
            return "User not found", 404

        # Get Ride History
        rides = list(db.ride.find({"user_id": user["user_id"]}))

        return render_template('profile.html', user=user, rides=rides)
    except Exception as e:
        print("Error:", e)
        flash("Failed to fetch profile details", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/wallet')
def wallet():
    try:
        email = session['email_id']


        # Fetch User Details
        user = db.user.find_one({"email": email})

        if not user:
            return "User not found", 404

        # Fetch Wallet Details
        wallet = db.wallet.find_one({"user_id": user["user_id"]})

        if not wallet:
            return "Wallet not found", 404

        return render_template('wallet.html', user=user, wallet=wallet)
    except Exception as e:
        print("Error:", e)
        flash("Failed to fetch wallet details", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/add-vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        reg_plate = request.form['reg_plate']
        name = request.form['name']
        battery = float(request.form['battery'])
        station_id = request.form['station_id']
        status = request.form['status']

        db.vehicle.insert_one({
            "reg_plate": reg_plate,
            "name": name,
            "battery": battery,
            "station_id": station_id,
            "status": status
        })
        return redirect('/add-vehicle')
    return render_template('add_vehicle.html')

@app.route('/location/<ride_id>')
def location(ride_id):
    
    print(ride_id)
    stations = list(db.stations.find({}, {"_id": 0, "station_id": 1, "name": 1, "latitude": 1, "longitude": 1}))
    return render_template('location.html', ride_id=ride_id, stations=stations)

# Define geofence boundaries (example)
GEOFENCE_CENTER = (23.0225, 72.5714)  # Center of Ahmedabad
GEOFENCE_RADIUS = 15000  # 15 km radius

# Store tracking info
user_tracking = {}

def is_outside_geofence(lat, lon):
    """Check if the user is outside geofence"""
    distance = geodesic((lat, lon), GEOFENCE_CENTER).km
    return distance > (GEOFENCE_RADIUS / 1000)  # Convert meters to km

@app.route('/track', methods=['POST'])
def track_location():
    """Track user location and apply penalty if needed"""
    data = request.json
    user_id = data['user_id']
    lat, lon = data['lat'], data['lon']
    
    if user_id not in user_tracking:
        user_tracking[user_id] = {
            'start_time': time.time(),
            'inside_geofence': True,
            'penalty_start': None,
            'distance': 0,
            'total_cost': 0,
            'violations': 0,
            'last_position': (lat, lon)
        }
    
    tracking = user_tracking[user_id]
    
    # Calculate distance from last position
    if tracking['last_position']:
        last_lat, last_lon = tracking['last_position']
        distance = geodesic((lat, lon), (last_lat, last_lon)).km
        tracking['distance'] += distance
    
    tracking['last_position'] = (lat, lon)
    
    # Check if user is outside the geofence
    if is_outside_geofence(lat, lon):
        if tracking['inside_geofence']:
            tracking['inside_geofence'] = False
            tracking['penalty_start'] = time.time()
            tracking['violations'] += 1
            return jsonify({
                "alert": "You have exited the allowed area! Return within 10 minutes to avoid penalties.",
                "violation": True,
                "violation_count": tracking['violations']
            })

        # Check if 10 minutes have passed
        elif time.time() - tracking['penalty_start'] >= 600:  # 10 minutes = 600 seconds
            tracking['cost_per_km'] = 50  # Increased penalty rate
            return jsonify({
                "alert": "Penalty applied: ₹50 per km for being outside allowed area",
                "penalty_applied": True,
                "cost_per_km": 50
            })
    else:
        if not tracking['inside_geofence']:
            tracking['inside_geofence'] = True
            tracking['penalty_start'] = None
            tracking['cost_per_km'] = 1.50  # Reset to normal rate
            return jsonify({
                "alert": "Welcome back to the allowed area! Normal rates restored.",
                "violation_cleared": True
            })

    # Calculate current fare based on distance and violations
    base_fare = tracking['distance'] * tracking.get('cost_per_km', 1.50)
    penalty_fare = tracking['violations'] * 100  # Additional penalty for each violation
    total_fare = base_fare + penalty_fare

    return jsonify({
        "status": "Tracking updated",
        "distance": round(tracking['distance'], 2),
        "base_fare": round(base_fare, 2),
        "penalty_fare": round(penalty_fare, 2),
        "total_fare": round(total_fare, 2),
        "violations": tracking['violations']
    })

@app.route('/start_ride/<ride_id>', methods=['POST'])
def start_ride(ride_id):
    try:

        ride1= db.ride.find({"r_id": int(ride_id)})
        print(ride1)
        if not ride1:
            return jsonify({"success": False, "message": "Ride not found"}), 404
        db.vehicle.update({"v_id": int(ride1[0]["v_id"])}, {"$set": {"status": "in-use"}})
        db.ride.update_one({"r_id": ride_id}, {"$set": {"status": "ongoing"}})
        return jsonify({"success": True, "message": "Ride started successfully!"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Failed to start ride."}), 500

@app.route('/end_ride/<ride_id>', methods=['POST'])
def end_ride(ride_id):
    try:
        data = request.json
        total_distance = data.get('total_distance', 0)
        total_fare = data.get('total_fare', 0)
        total_penalty = data.get('total_penalty', 0)
        base_payment = data.get('base_payment', 0)

        # Calculate total payment including penalties
        total_payment = base_payment + total_penalty
        total_profit = total_payment * 0.20  # 20% profit margin

        # Get ride details first
        ride = db.ride.find_one({"r_id": int(ride_id)})
        if not ride:
            return jsonify({"error": "Ride not found"}), 404

        # Get user wallet
        user = db.user.find_one({"user_id": ride["user_id"]})
        if not user:
            return jsonify({"error": "User not found"}), 404

        wallet = db.wallet.find_one({"user_id": user["user_id"]})
        if not wallet:
            return jsonify({"error": "Wallet not found"}), 404

        # Check if user has sufficient balance
        if wallet["amount"] < total_payment:
            return jsonify({"error": "Insufficient balance in wallet"}), 400

        # Start a transaction-like operation
        try:
            # Update ride status and details
            ride_update = db.ride.update_one(
                {"r_id": int(ride_id)},
                {
                    "$set": {
                        "status": "completed",
                        "total_distance": total_distance,
                        "total_payment": total_payment,
                        "total_profit": total_profit,
                        "end_time": datetime.now()
                    }
                }
            )

            if ride_update.modified_count == 0:
                return jsonify({"error": "Failed to update ride status"}), 500

            # Update vehicle status
            vehicle_update = db.vehicle.update(
                {"v_id": int(ride["v_id"])},
                {"$set": {"status": "Available"}}
            )

            # if vehicle_update.modified_count == 0:
            #     return jsonify({"error": "Failed to update vehicle status"}), 500

            # Update wallet balance
            wallet_update = db.wallet.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"amount": -total_payment}}
            )

            if wallet_update.modified_count == 0:
                return jsonify({"error": "Failed to update wallet"}), 500

            return jsonify({
                "message": "Ride ended successfully",
                "total_distance": total_distance,
                "base_payment": base_payment,
                "penalty": total_penalty,
                "total_payment": total_payment,
                "total_profit": total_profit
            })

        except Exception as e:
            print(f"Error in transaction: {str(e)}")
            return jsonify({"error": "Failed to complete ride end process"}), 500

    except Exception as e:
        print(f"Error in end_ride: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/scan_qr_live')
def scan_qr_live():
    vehicle_id = request.args.get('vehicle_id')
    return render_template('scan_qr_live.html', vehicle_id=vehicle_id)

@app.route('/process_qr/<clicked_vehicle_id>', methods=['POST'])
def process_qr(clicked_vehicle_id):
    try:
        data = request.json
        vehicle_id = data.get('vehicle_id')

        if not vehicle_id:
            return jsonify({"success": False, "message": "No vehicle ID provided"})

        # Ensure user is logged in
        user_email = session.get('email_id')
        if not user_email:
            return jsonify({"success": False, "message": "User not logged in"})

        # Validate QR Code and check vehicle availability
        vehicle = db.vehicle.find_one({"v_id": int(vehicle_id), "status": "Available"})
        
        if not vehicle:
            return jsonify({"success": False, "message": "Vehicle not available or does not exist"})
        
        if str(vehicle_id) != str(clicked_vehicle_id):
            return jsonify({"success": False, "message": "Vehicle didn't match"})
        
        # Start the ride
        user = db.user.find_one({"email": user_email})
        rideid = db.ride.find_one(sort=[("r_id", -1)])
        
        ride_data = {
            "r_id": rideid["r_id"] + 1,
            "user_id": user["user_id"],
            "v_id": vehicle_id,
            "time": datetime.now(),
            "status": "ongoing"
        }
        
        result = db.ride.insert_one(ride_data)
        r_id = result.inserted_id
        r_id = db.ride.find_one({"_id": r_id})["r_id"]
        
        # Update vehicle status
        db.vehicle.update_one(
            {"v_id": vehicle_id},
            {"$set": {"status": "in-use"}}
        )
        
        return jsonify({"success": True, "message": "Ride started successfully!", "ride_id": r_id})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": "Failed to start ride. Please try again."})

@app.route('/add-funds', methods=['GET', 'POST'])
def add_funds():
    if request.method == 'POST':
        user_id = session.get('user_id')
        amount = float(request.form.get('amount', 0))

        if amount <= 0:
            flash('Invalid amount. Please enter a positive value.', 'error')
            return redirect('/add-funds')

        # Update user balance in database
        db.wallet.update_one(
            {"user_id": user_id},
            {"$inc": {"amount": amount}}
        )

        flash(f'₹{amount:.2f} added to your account successfully!', 'success')
        return redirect('/wallet')

    return render_template('add_funds.html')
@app.route('/analysis')
def analysis():
    return render_template('data_analysis.html')

if __name__ == '__main__':
    app.run(debug=True)