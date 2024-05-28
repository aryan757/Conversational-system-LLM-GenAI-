import streamlit as st
import csv
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from dotenv import load_dotenv
import os

load_dotenv()

# Ensure the 'uploaded_images' directory exists
os.makedirs("uploaded_images", exist_ok=True)

# Initialize session state for intent_classification and follow-up questions
if 'intent_classification' not in st.session_state:
    st.session_state['intent_classification'] = None
if 'follow_up_responses' not in st.session_state:
    st.session_state['follow_up_responses'] = {}
if 'current_question_index' not in st.session_state:
    st.session_state['current_question_index'] = 0

follow_up_questions = {
    "Child safety": [
        "Child's name",
        "Child's age",
        "Description of clothing last worn",
        "Last known location and time",
        "Any known associates or suspects"
    ],
    "Cyber crime incident": [
        "Type of cyber crime",
        "Description of the incident",
        "Date and time of the incident",
        "Any known suspects or source of the attack",
        "Account number (if bank involved)(Optional)",
        "Bank details (Name,Branch,IFSC code.)(Optional)"
    ],
    "Women help desk": [
        "Nature of the incident",
        "Time and location of the incident",
        "Description of the perpetrator",
        "Immediate support needed",
        "Any witnesses or evidence available"
    ],
    "Public healthcare": [
        "Type of health concern",
        "Number of people affected",
        "Location of the healthcare issue",
        "Urgency of the situation",
        "Availability of medical assistance"
    ],
    "Road accident": [
        "Location of the accident",
        "Time of the accident",
        "Vehicles involved",
        "Injuries or fatalities",
        "Witnesses or available surveillance footage"
    ],
    "murder / serious crime incident": [
        "Description of the incident",
        "Date and time of the incident",
        "Location of the incident",
        "Victim information",
        "Suspect information",
        "Evidence or leads"
    ],
    "Fire accident": [
        "Location of the fire",
        "Time the fire started",
        "Known cause of the fire",
        "Injuries or fatalities",
        "Current status of the fire"
    ],
    "issue recorded":[
        "Description of the incident",
        "Timing",
        "Help needed (Yes/No)",
        "current location"
    ]
}

# Function to save uploaded file to local filesystem
def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join("uploaded_images", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"An error occurred while saving the file: {e}")
        return False

# Function to initialize and train the chatbot
def initialize_chatbot():
    chatbot = ChatBot('PoliceChatBot')
    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train('chatterbot.corpus.english')  # Train the chatbot with English corpus
    return chatbot

# Initialize chatbot
chatbot = initialize_chatbot()

# Function to analyze query using the chatbot
def analyze_query(user_query):
    response = chatbot.get_response(user_query)
    return response.text

# Function to display follow-up questions
def display_follow_up_questions(intent_classification):
    if intent_classification in follow_up_questions:
        questions = follow_up_questions[intent_classification]
        current_index = st.session_state.get('current_question_index', 0)

        if current_index == 0:
            st.session_state['follow_up_responses'] = {question: "" for question in questions}

        if current_index < len(questions):
            question = questions[current_index]
            st.markdown(f"**Bot**: {question}?")  # Display the question as if the chatbot is asking

            user_response_key = f"{question}_user_response"
            user_response = st.text_input("**You**:", st.session_state['follow_up_responses'].get(question, ""), key=user_response_key)
            st.session_state['follow_up_responses'][question] = user_response

            if st.button("Next"):
                st.session_state['current_question_index'] += 1
                if current_index == len(questions) - 1:
                    st.success("Thank you for providing the details.")
                st.experimental_rerun()

        else:
            st.warning("No more follow-up questions.")

    else:
        st.warning("No follow-up questions for the given intent classification.")

    
# Streamlit front-end
st.title("Police सेवा portal System (Conversational Chatbot)")

# Chat interface
messages = st.empty()  # Create an empty container to display the chat messages

# Initialize session state for user name, phone, and query
if 'user_query' not in st.session_state:
    st.session_state['user_query'] = ''

# Initial prompt
if not st.session_state['user_query']:
    messages.markdown("**Bot**: Hello! I'm a conversational bot designed to assist you with various incidents and emergencies. Please enter your query, and I'll do my best to help you.")

# Get user input
user_input = st.text_input("**You**:", st.session_state['user_query'])

# Update user query in session state
st.session_state['user_query'] = user_input
if user_input:
    # Analyze the user's query
    response = analyze_query(user_input)
    messages.markdown(f"**Bot**: {response}")

    # If an intent classification is present, display follow-up questions one by one
    if response and response in follow_up_questions:
        display_follow_up_questions(response)

if st.button("Submit Follow-up Information"):
    # Handle the submission of follow-up information
    csv_filename = "user_data.csv"  # You can modify this to use anonymous data if needed
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            '',
            '',
            st.session_state['user_query'],
            st.session_state['intent_classification'],
            *st.session_state['follow_up_responses'].values()])
    st.success("Follow-up data successfully saved to CSV file.")

    # Clear the session state after successful submission
    del st.session_state['intent_classification']
    del st.session_state['follow_up_responses']
    st.session_state['current_question_index'] = 0
    st.session_state['user_query'] = ''
    messages.markdown("Bot: Thank you for providing the details. Your information has been recorded.")
