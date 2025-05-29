# web_app_new.py

print("DEBUG: Starting web_app_new.py script...") # Keep this for debugging

from flask import Flask, render_template_string, request, url_for, jsonify
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amazon AI Chatbot</title>
    <link rel="stylesheet" href="/static/style.css">
    <link rel="icon" href="/static/Favicon.png" type="image/png">
</head>
<body>
    <div class="container">
        <header>
            <h1>Your Personal Amazon Assistant</h1>
            <p>Your intelligent partner for Amazon selling success.</p>
        </header>
        <div class="chat-box" id="chatBox">
            <p class="message bot-msg"><b>Assistant:</b> Hello! I'm your Amazon AI Assistant. How can I help you with your Amazon selling journey today?</p>
            </div>
        <div id="loadingIndicator" style="display: none;">...</div> <form id="chatForm" class="input-area"> <textarea name="user_input" placeholder="Ask me anything about Amazon selling..." rows="1" required></textarea>
            <div class="button-group">
                <button type="submit" class="send-btn">Send</button>
                <button type="button" id="clearChatBtn" class="clear-btn">Clear Chat</button>
            </div>
        </form>
    </div>

    <script>
        const chatBox = document.getElementById("chatBox");
        const loadingIndicator = document.getElementById("loadingIndicator");
        const userInput = document.querySelector('textarea[name="user_input"]');
        const chatForm = document.getElementById("chatForm");
        const clearChatBtn = document.getElementById("clearChatBtn");

        // Function to scroll to the bottom of the chat box smoothly
        function scrollToBottom() {
            chatBox.scrollTo({
                top: chatBox.scrollHeight,
                behavior: 'smooth' // Smooth scrolling!
            });
        }

        // Function to show the loading indicator
        function showLoading() {
            loadingIndicator.style.display = 'block';
            scrollToBottom();
        }

        // Function to hide the loading indicator
        function hideLoading() {
            loadingIndicator.style.display = 'none';
        }

        // Initially hide the loading indicator and scroll to bottom on page load
        document.addEventListener('DOMContentLoaded', hideLoading);
        document.addEventListener('DOMContentLoaded', scrollToBottom);

        // Dynamic Textarea Resizing
        userInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            scrollToBottom(); // Keep chat scrolled to bottom as user types
        });

        // Handle form submission via AJAX
        chatForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // IMPORTANT: Prevent the default form submission (page reload)

            const userMessage = userInput.value.trim();
            if (userMessage === "") return; // Don't send empty messages

            // 1. Add user message to chat box immediately
            const userMsgElement = document.createElement('p');
            userMsgElement.className = 'message user-msg';
            userMsgElement.innerHTML = `<b>You:</b> ${userMessage}`;
            chatBox.appendChild(userMsgElement);
            scrollToBottom();

            userInput.value = ''; // Clear input field
            userInput.style.height = 'auto'; // Reset textarea height after clearing
            showLoading(); // Show loading indicator

            try {
                // 2. Send message to Flask backend using fetch (AJAX)
                const response = await fetch('/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ user_input: userMessage })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json(); // Get the JSON response from Flask

                // 3. Add bot response to chat box
                const botMsgElement = document.createElement('p');
                botMsgElement.className = 'message bot-msg';
                // Flask will send pre-formatted HTML (thanks to markdown2), so use innerHTML
                botMsgElement.innerHTML = `<b>Assistant:</b> ${data.bot_response}`;
                chatBox.appendChild(botMsgElement);

            } catch (error) {
                console.error('Error sending message:', error);
                // Display a user-friendly error message in the chatbox if something goes wrong
                const errorMsgElement = document.createElement('p');
                errorMsgElement.className = 'message bot-msg';
                errorMsgElement.innerHTML = `<b>Assistant:</b> Oh dear, something went wrong! Please try again. (Error: ${error.message})`;
                chatBox.appendChild(errorMsgElement);
            } finally {
                // 4. Always hide loading indicator and scroll to bottom
                hideLoading();
                scrollToBottom();
            }
        });

        // Clear Chat Functionality (updated for AJAX)
        clearChatBtn.addEventListener("click", function() {
            if (confirm("Are you sure you want to clear the chat history?")) {
                chatBox.innerHTML = ''; // Clear messages from the display
                // Send a request to the server to clear the actual chat_history
                fetch('/clear_history', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.status); // Log status from server
                        // Optionally add a "Chat history cleared" message to chatBox if needed
                        const clearedMsgElement = document.createElement('p');
                        clearedMsgElement.className = 'message bot-msg';
                        clearedMsgElement.innerHTML = '<b>Assistant:</b> Chat history cleared!';
                        chatBox.appendChild(clearedMsgElement);
                        scrollToBottom();
                    })
                    .catch(error => console.error('Error clearing history:', error));
            }
        });
    </script>
</body>
</html>
"""

# web_app_new.py - Add chatbot function here

# ... (HTML_TEMPLATE block ends here) ...

# Route for the main chat page (GET request to load the page)
@app.route('/', methods=['GET'])
def index():
    global chat_history # Ensure we're using the global variable
    # Initial chat history can be reset or loaded from a session here if needed.
    # For simplicity, we'll let the initial welcome message come from HTML and keep chat_history for subsequent turns.
    return render_template_string(HTML_TEMPLATE, chat_history=chat_history)

# New route for handling AJAX messages (POST request)
# New route for handling AJAX messages (POST request)
@app.route('/send_message', methods=['POST'])
def send_message():
    global chat_history # We need to tell Python we're using the global chat_history list

    try:
        # Get user input from the JSON request sent by JavaScript
        data = request.get_json()
        user_message = data['user_input']

        # Add user message to history (for server-side tracking, though UI handles display)
        # Ensure proper format for Gemini API: {'role': 'user', 'parts': ['text']}
        chat_history.append({'role': 'user', 'parts': [user_message]})

        # Start a new chat session with the updated history for each request
        # This ensures Gemini has context from previous turns
        # Convert history to the format expected by model.start_chat()
        formatted_history_for_gemini = []
        for msg in chat_history:
            if msg['role'] == 'user':
                formatted_history_for_gemini.append({'role': 'user', 'parts': [msg['parts'][0]]})
            elif msg['role'] == 'model':
                
                if msg['role'] == 'user':
                    formatted_history_for_gemini.append({'role': 'user', 'parts': [msg['text']]})
                elif msg['role'] == 'model':
                    # Convert previously stored plain text bot response to Content object for Gemini
                    formatted_history_for_gemini.append({'role': 'model', 'parts': [msg['text']]})

        chat_session = model.start_chat(history=formatted_history_for_gemini)

        # Get Gemini's response
        gemini_response_object = chat_session.send_message(user_message)
        gemini_response_text = gemini_response_object.text # Get the plain text response

        # Convert Gemini's plain text response to HTML for better formatting in the UI
        formatted_response_html = markdown2.markdown(gemini_response_text, extras=["fenced-code-blocks", "tables", "footnotes"])

        # Add bot's *plain text* response to server-side chat_history
        chat_history.append({'role': 'model', 'text': gemini_response_text}) # Store plain text for history context

        # Return the formatted HTML bot response as JSON to the JavaScript
        return jsonify({'bot_response': formatted_response_html})

    except Exception as e:
        # Handle potential errors during processing
        error_message = f"Oh dear, something went wrong! Error: {e}. Please try again."
        print(f"Error in send_message: {e}") # Log error for debugging
        # Return the error message as JSON to the JavaScript, with a 500 status code
        return jsonify({'bot_response': error_message}), 500
    
# Route to clear chat history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    global chat_history
    chat_history = []
    # Return a JSON response for the AJAX call
    return jsonify({'status': 'Chat history cleared'})


# This makes our web server actually start running!
if __name__ == '__main__':
    app.run(debug=True) # debug=True helps us see errors easily



