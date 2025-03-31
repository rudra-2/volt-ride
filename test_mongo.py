from pymongo import MongoClient

def test_mongo_connection():
    try:
        # MongoDB Configuration
        client = MongoClient("mongodb+srv://mhpatel2026:IgYD8BSAHN67J9PL@cluster0.y2dqwmk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["voltride"]

        # Test the connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully!")

        # Insert a test document
        test_collection = db["test_collection"]
        test_document = {"name": "Test User", "email": "testuser@example.com"}
        result = test_collection.insert_one(test_document)
        print(f"Inserted document with ID: {result.inserted_id}")

        # Retrieve the test document
        retrieved_document = test_collection.find_one({"_id": result.inserted_id})
        print("Retrieved document:", retrieved_document)

        # Clean up (delete the test document)
        test_collection.delete_one({"_id": result.inserted_id})
        print("Test document deleted successfully!")

    except Exception as e:
        print("Error connecting to MongoDB:", e)

if __name__ == "__main__":
    test_mongo_connection()