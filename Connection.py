from pymongo import MongoClient, InsertOne
from pymongo.errors import ConnectionFailure, BulkWriteError, DuplicateKeyError

# MongoDB Connection
uri = "mongodb+srv://mhpatel2026:ASDFGHJKL@cluster0.y2dqwmk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, serverSelectionTimeoutMS=30000, socketTimeoutMS=30000, connectTimeoutMS=30000)

# Test connection
try:
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except ConnectionFailure as e:
    print(f"❌ Connection failed: {e}")

# Access database
db = client["hk"]  # Ensure "hk" is the correct DB name

# Function to insert data safely in batches
def batch_insert(collection, data):
    try:
        if data:
            collection.insert_many(data, ordered=False)
            print(f"✅ Inserted into {collection.name}")
    except BulkWriteError as e:
        print(f"⚠️ BulkWriteError in {collection.name}: {e.details}")

# Function to insert records
def f1():
    batch_insert(db.counters, [
        { "id": "charging_ports", "seq": 5 },
        { "id": "ride", "seq": 10 },
        { "id": "tracking", "seq": 3 },
        { "id": "user", "seq": 3 },
        { "id": "transaction", "seq": 3 },
        { "id": "vehicle", "seq": 4 },
        { "id": "wallet", "seq": 2 },
        { "id": "stations", "seq": 2 }
    ])
    
    batch_insert(db.charging_ports, [
        { "port_id": 1, "station_id": 1, "status": "Available", "vehicle_id": "", "battery": "" },
        { "port_id": 2, "station_id": 1, "status": "Available", "vehicle_id": "", "battery": "" },
        { "port_id": 3, "station_id": 1, "status": "Occupied", "vehicle_id": 2, "battery": 45 },
        { "port_id": 4, "station_id": 1, "status": "Available", "vehicle_id": "", "battery": "" }
    ])

def f2():
    batch_insert(db.ride, [
        { "r_id": 1, "user_id": 2, "v_id": 1, "time": "10:00:00", "date": "2025-03-20", "status": "Completed", "payment": 100, "profit": 30 },
        { "r_id": 2, "user_id": 2, "v_id": 2, "time": "12:30:00", "date": "2025-03-21", "status": "Completed", "payment": 150, "profit": 50 },
        { "r_id": 3, "user_id": 2, "v_id": 3, "time": "22:55:35", "date": "2025-03-22", "status": "ongoing", "payment": 0, "profit": 0 }
    ])

    try:
        db.stations.insert_one({
            "station_id": 1, "name": "PDEU", "latitude": 50, "longitude": 50, "master_id": 1
        })
    except DuplicateKeyError:
        print("⚠️ Station already exists.")

    batch_insert(db.tracking, [
        { "track_id": 1, "user_id": 2, "v_id": 1, "latitude": 50.1234, "longitude": 50.5678 },
        { "track_id": 2, "user_id": 2, "v_id": 2, "latitude": 51.1234, "longitude": 51.5678 }
    ])

def f3():
    batch_insert(db.transaction, [
        { "t_id": 1, "user_id": 2, "w_id": 1, "method": "Credit Card", "amount": 100 },
        { "t_id": 2, "user_id": 2, "w_id": 1, "method": "UPI", "amount": 150 }
    ])

    batch_insert(db.user, [
        {
            "user_id": 1, "role": "master", "first_name": "rm", "last_name": "patel",
            "email": "mhpatel2026@gmail.com", "mobile": 8468788788, "password": "000000",
            "licence_photo": "https://www.gstatic.com/mobilesdk/240501_mobilesdk/firebase_28dp.png",
            "licence_number": "11111111", "approval": "pending"
        },
        {
            "user_id": 2, "role": "user", "first_name": "acs", "last_name": "ascd",
            "email": "codergirgit@gmail.com", "mobile": 9876543210, "password": "12345",
            "licence_photo": "Bombay.jpg", "licence_number": "213654", "approval": "pending"
        }
    ])

def f4():
    batch_insert(db.vehicle, [
        { "v_id": 1, "reg_plate": "GJ01RL1111", "name": "VoltRide X1", "battery": 90, "station_id": 1, "status": "Available" },
        { "v_id": 2, "reg_plate": "GJ02CD5678", "name": "EV-Two", "battery": 51, "station_id": 1, "status": "Occupied" },
        { "v_id": 3, "reg_plate": "GJ03EF9101", "name": "EV-Three", "battery": 100, "station_id": 1, "status": "in-use" }
    ])

    try:
        db.wallet.insert_one({ "w_id": 1, "user_id": 2, "amount": 250 })
    except DuplicateKeyError:
        print("⚠️ Wallet already exists.")

def f5():
    indexes = [
        ("charging_ports", "port_id"),
        ("ride", "r_id"),
        ("stations", "station_id"),
        ("tracking", "track_id"),
        ("transaction", "t_id"),
        ("user", "user_id"),
        ("vehicle", "v_id"),
        ("wallet", "w_id")
    ]

    for collection, field in indexes:
        db[collection].create_index([(field, 1)], unique=True)
        print(f"✅ Created unique index on {collection}.{field}")

    # Additional indexes
    db.charging_ports.create_index([("station_id", 1)])
    db.ride.create_index([("user_id", 1), ("v_id", 1)])
    db.tracking.create_index([("user_id", 1), ("v_id", 1)])
    db.transaction.create_index([("user_id", 1), ("w_id", 1)])
    db.vehicle.create_index([("station_id", 1)])
    db.wallet.create_index([("user_id", 1)])
    db.user.create_index([("email", 1), ("mobile", 1)], unique=True)

# Execute functions
f1()
f2()
f3()
f4()
f5()
