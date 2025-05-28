import google.generativeai as genai
import os


# This is where you'll put your secret Gemini key!
# It's like telling our robot its secret password.
# Replace 'YOUR_GEMINI_API_KEY' with the key you saved earlier.
genai.configure(api_key="AIzaSyC7iGgDgvMNTAQ8kOnt_qxz-1YBTwWJ5No")

# This is the brain of our robot. We'll tell it how to act.
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# This is like our robot's memory!
# It will remember what we talked about before.
chat = model.start_chat(history=[])

# This is a special starting message for our robot.
# We're telling it to be an Amazon Seller Assistant.
print("Hello! I am your Amazon Seller Assistant. How can I help you today?")
print("Type 'exit' to quit.")

# This is the main part where our robot talks to you!
while True: # This means "keep doing this forever, until I say stop!"
    user_message = input("You: ") # This waits for you to type something and press Enter.

    if user_message.lower() == 'exit': # If you type 'exit' (even 'Exit' or 'EXIT'), it stops.
        print("Amazon Seller Assistant: Goodbye! Happy selling!")
        break # This is like saying "STOP THE LOOP!"

    try:
        # This is where our robot sends your message to the Gemini brain and gets an answer!
        response = chat.send_message(user_message)
        # And then our robot says the answer out loud!
        print(f"Amazon Seller Assistant: {response.text}")
    except Exception as e:
        # If something goes wrong, our robot will tell us!
        print(f"Amazon Seller Assistant: Oh dear, something went wrong! Error: {e}")
        print("Please try again or check your internet connection.")