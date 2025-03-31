import requests
from groq import Groq
import os
from groq import Client  # Import the Client class from the groq library

# Store your Groq API key here
GROQ_API_KEY = "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"  # Replace with your actual key
GROQ_API_URL = "https://api.groq.com/v1/chat/completions"

# Predefined FAQs
FAQ_RESPONSES = {
    "how to rent a vehicle": "To rent a vehicle, log in, select a vehicle, and confirm the booking.",
    "what are the rental charges": "Rental charges start at $5 per hour with additional per-mile costs.",
    "how do i contact support": "You can reach support at support@voltride.com."
}

# Function to get AI response from Groq
def get_groq_response(user_input):

            os.environ["GROQ_API_KEY"] = "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"  
            client = Client(api_key=os.getenv("GROQ_API_KEY"))
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                    "role": "user",
                    "content": "Welcome to **Volt Ride**, your smart EV rental service! 🚀 Our platform ensures a seamless experience from registration to ride completion. Users sign up, verify their email via OTP, and log in to book available electric vehicles. Once booked, the vehicle unlocks through the app, and the ride begins with real-time tracking and geofencing for safety. At ride completion, the fare is calculated based on usage and deducted from the in-app wallet, which can be recharged via digital payments. Our AI-powered customer support bot is available for quick assistance with booking, ride issues, or payments. Users can end their ride at designated stations and provide feedback to enhance our service. Experience a **smart, sustainable, and hassle-free** way to travel with **Volt Ride! ⚡🚲 .. accorind to this summar as this question > "+user_input,
                    },
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            
            response_text = ""
            for chunk in completion:
                response_text += chunk.choices[0].delta.content or ""

            if response_text:
                print(response_text)
                #self.speak(response_text)
                # print(response_text)
            else:
                print("I received no meaningful response. Please try again.")


# Terminal chat loop
def chat():
    print("VoltRide Customer Support Bot (Type 'exit' to quit)")
    
    while True:
        user_message = input("You: ").strip().lower()
        
        if user_message == "exit":
            print("Chatbot: Goodbye! Have a great day!")
            break
        
        # Check FAQs first
        for question, answer in FAQ_RESPONSES.items():
            if question in user_message:
                print(f"Chatbot: {answer}")
                break
        else:
            # If no predefined answer, ask Groq AI
            ai_response = get_groq_response(user_message)
            print(f"Chatbot: {ai_response}")

# Run chatbot in terminal
if __name__ == "__main__":
    chat()
