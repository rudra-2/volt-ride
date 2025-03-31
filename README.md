# ⚡ VoltRide - Intelligent Ride Management System

VoltRide is a smart and efficient ride management platform designed for electric vehicle (EV) rentals. With advanced geofencing technology and real-time tracking, it ensures secure and hassle-free rides for users while providing automated management for station masters.

🚀 **Built by Team Infinity Nueral**  
🏆 Developed at **HackNUthon**  
👨‍💻 **Team Leader:** [Rudra Patel](https://github.com/rudra-2)  
🤝 **Team Members:**   
- Nihanshu Bhanderi
- Dhruvil Patel  
- Jarnil Patel  
---

## 🌟 Features

- **Geofencing Technology**: Ensures rides are completed within authorized areas.  
- **Real-Time GPS Tracking**: Track vehicle location with live updates.  
- **Station Master Dashboard**: Monitor active rides, battery status, and vehicle availability.  
- **Penalty Management**: Auto-calculates penalties for late returns or damaged vehicles.  
- **Admin Dashboard**: View charging station details, vehicle information, and reports.  
- **OTP Login System**: Secure login via Gmail OTP authentication.  
- **Payment Management**: Transparent cost and penalty calculation for users.  

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript (Bootstrap)  
- **Backend:** Flask (Python)  
- **Database:** MySQL (XAMPP)  
- **Authentication:** Gmail OTP (via Twilio)  

---

## 🚀 Installation and Setup

1. **Clone the Repository**
    ```
    git clone https://github.com/rudra-2/volt-ride.git
    cd VoltRide
    ```

2. **Create and Activate Virtual Environment**
    ```
    python -m venv env
    source env/bin/activate  # For Linux/macOS
    env\Scripts\activate     # For Windows
    ```

3. **Install Dependencies**
    ```
    pip install -r requirements.txt
    ```

4. **Configure Database**
    - Install XAMPP and start MySQL.  
    - Create a database named `voltride`.  
    - Import `voltride.sql` using phpMyAdmin or MySQL CLI.  

5. **Set Environment Variables**
    ```
    export FLASK_APP=app.py
    export FLASK_ENV=development
    ```

6. **Run the Application**
    ```
    flask run
    ```

7. **Access the Application**
    - Visit: `http://localhost:5000`

---
