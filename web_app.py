# web_app_new.py

print("DEBUG: Starting web_app_new.py script...") # Keep this for debugging

from flask import Flask, render_template_string, request, url_for
import google.generativeai as genai
import os
import markdown2 # Add this new import!

# Important: Put your Gemini API key here again!
# Make sure it's inside the quotation marks "".
genai.configure(api_key="AIzaSyC7iGgDgvMNTAQ8kOnt_qxz-1YBTwWJ5No")

# Choose our robot's brain model (the one that worked for you!)
# Define a system instruction to restrict the bot's scope
SYSTEM_INSTRUCTION = (
    "You are an AI chatbot specializing in Amazon Seller Assistance. "
    "Your purpose is to provide helpful and accurate information related to selling on Amazon, "
    "including topics such as product listing, advertising, FBA, inventory management, "
    "seller policies, account health, and general e-commerce strategies specific to Amazon. "
    "If a user asks a question that is outside the scope of Amazon Seller Assistance, "
    "you must politely decline to answer, stating that you are an Amazon Seller Assistant "
    "and can only provide information relevant to selling on Amazon. "
    "Do not answer general knowledge questions, personal questions, or questions unrelated to Amazon selling."
)

# Choose our robot's brain model and provide the system instruction
model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=SYSTEM_INSTRUCTION)
# This is like setting up our website's main door
app = Flask(__name__)

# This is our robot's "memory" for the conversation.
chat_history = []

# Add the HTML_TEMPLATE block here:
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Amazon AI Chatbot</title>
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='Favicon.png') }}">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Your Personal Amazon Assistant</h1>
        <p class="tagline">Your intelligent partner for Amazon selling success.</p>
        <div class="chat-box" id="chatBox">
            <div class="chat-box" id="chatBox">
            <div id="loadingIndicator" class="loading-indicator">...</div> 
            {% for message in chat_history %}
                {% if message.role == 'user' %}
                    <p class="message user-msg"><b>You:</b> {{ message.text }}</p>
                {% else %}
                    <p class="message bot-msg"><b>Assistant:</b> {{ message.text | safe }}</p>
                {% endif %}
            {% endfor %}
        </div>
        <form method="POST" action="/" class="input-area" onsubmit="showLoading();">
            <textarea name="user_input" placeholder="Ask me anything about Amazon selling..." autocomplete="off" autofocus rows="1"></textarea> ```
            <input type="submit" value="Send">
            <button type="button" id="clearChatBtn">Clear Chat</button> 
        </form>
    </div>

   <script>
        var chatBox = document.getElementById("chatBox");
        var loadingIndicator = document.getElementById("loadingIndicator");
        chatBox.scrollTop = chatBox.scrollHeight;

        var chatBox = document.getElementById("chatBox");
        var loadingIndicator = document.getElementById("loadingIndicator");
        var userInput = document.querySelector('textarea[name="user_input"]'); // Get the textarea
        chatBox.scrollTop = chatBox.scrollHeight;

        // Dynamic Textarea Resizing
        userInput.addEventListener('input', function() {
            this.style.height = 'auto'; // Reset height to recalculate
            this.style.height = (this.scrollHeight) + 'px'; // Set height based on scrollHeight
            chatBox.scrollTop = chatBox.scrollHeight; // Keep chat scrolled to bottom
        });

        // Function to show the loading indicator
        function showLoading() {
            loadingIndicator.style.display = 'block'; // Show the indicator
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom to show it
        }

        // Function to hide the loading indicator
        function hideLoading() {
            loadingIndicator.style.display = 'none'; // Hide the indicator
        }

        // Initially hide the loading indicator when the page loads
        document.addEventListener('DOMContentLoaded', hideLoading);

        // Clear Chat Functionality (existing code)
        document.getElementById("clearChatBtn").addEventListener("click", function() {
            if (confirm("Are you sure you want to clear the chat history?")) {
                chatBox.innerHTML = '';
                fetch('/clear_history', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.status);
                    })
                    .catch(error => console.error('Error clearing history:', error)
                );
            }
        });
    </script>
</body>
</html>
"""

# web_app_new.py - Add chatbot function here

# ... (HTML_TEMPLATE block ends here) ...

# This tells our web server what to do when someone visits the main page "/"
@app.route('/', methods=['GET', 'POST'])
def chatbot():
    global chat_history # We need to tell Python we're using the global chat_history list
    # Initialize response here so it always exists
    response_text_to_display = "" # This will hold the text we want to show as bot response

    if request.method == 'POST':
        user_message = request.form['user_input']
        if user_message.lower() == 'exit':
            # For a web app, 'exit' usually means closing the browser tab,
            # or we could make it clear the history. For now, it just won't do anything special.
            pass
        else:
            try:
                # Add user message to history
                chat_history.append({'role': 'user', 'text': user_message})

                # Start a new chat session with the updated history for each request
                # This is a simple way to maintain conversation in a basic web app
                # For more complex apps, we'd use session IDs or databases.
                chat_session = model.start_chat(history=[
                    {'role': 'user', 'parts': [msg['text']]} if msg['role'] == 'user' else {'role': 'model', 'parts': [msg['text']]}
                    for msg in chat_history
                ])

                gemini_response = chat_session.send_message(user_message) # Renamed to gemini_response
                # Convert Gemini's response text to HTML for better formatting
                response_text_to_display = markdown2.markdown(gemini_response.text, extras=["fenced-code-blocks", "tables", "footnotes"])

                # Add bot response (now in HTML) to history
                chat_history.append({'role': 'model', 'text': response_text_to_display})

            except Exception as e:
                # If an error occurs, the error message is what we want to display
                response_text_to_display = f"Oh dear, something went wrong! Error: {e}. Please try again or check your internet connection."
                chat_history.append({'role': 'model', 'text': response_text_to_display})

    # Render the HTML template, passing the chat history to display messages
    return render_template_string(HTML_TEMPLATE, chat_history=chat_history)

# New route to clear chat history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    global chat_history
    chat_history = [] # Reset the global chat history
    return {'status': 'Chat history cleared'} # Send a success message back to JavaScript

# This makes our web server actually start running!
if __name__ == '__main__':
    app.run(debug=True) # debug=True helps us see errors easily



