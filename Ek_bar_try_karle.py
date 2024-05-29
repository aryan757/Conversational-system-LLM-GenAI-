import streamlit as st
from streamlit_chat import message
import csv
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure the 'uploaded_images' directory exists
os.makedirs("uploaded_images", exist_ok=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

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

# Function to perform sentiment analysis and incident classification
def analyze_query(user_query, user_name, user_phone):
    api_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
    if not api_token:
        raise ValueError("Hugging Face API token not found in environment variables.")

    prompt_template = """
        Analyze the sentiment and content of the following user query. Classify the incident into one of the specified categories and extract relevant entities, including the location:

        Categories:
        - Cyber crime incident
        - Women help desk
        - Public healthcare
        - Fire accident
        - Road accident
        - Child safety
        - murder / serious crime incident

        Instructions:
        1. Determine the most appropriate category for the incident based on the sentiment and content of the user query, if failed to classify then give the response as "issue recorded"  
        2. Identify and extract entities such as location, time, or individuals involved.

        User Name: "{user_name}"
        User Phone: "{user_phone}"
        User Query: "{user_query}"

        Response Format:

        - Intent Classification: 
        - Extracted Entities:
          - Location: 
          - Other Details: 
    """

    prompt = PromptTemplate.from_template(prompt_template)
    chain = LLMChain(
        llm=HuggingFaceHub(repo_id='mistralai/Mistral-7B-Instruct-v0.2', model_kwargs={'temperature': 0.7, 'max_new_tokens': 250}),
        prompt=prompt
    )
    result = chain.run(user_query=user_query, user_name=user_name, user_phone=user_phone)
    return result

    
def display_follow_up_questions(intent_classification):
    if intent_classification in follow_up_questions:
        questions = follow_up_questions[intent_classification]
        follow_up_responses = {}

        for i, question in enumerate(questions, start=1):
            st.write(f"Question {i}:")
            user_input = st.text_input(question, key=f"follow_up_{intent_classification}_{i}")

            if user_input:
                follow_up_responses[question] = user_input
                st.session_state.chat_history.append(message(user_input, is_user=True))
                st.session_state.chat_history.append(message(question))

        if follow_up_responses:
            return follow_up_responses
        else:
            st.warning("No follow-up questions answered.")
            return {}
    else:
        st.warning("No follow-up questions for the given intent classification.")
        return {}


# Streamlit front-end
st.title("Police सेवा portal System (Conversational)")

# Display greeting message
st.session_state.chat_history.append(message("Hello! Welcome to the Police सेवा portal System. How can I assist you today?", is_user=False))

# Display chat history
for chat_message in st.session_state.chat_history:
    st.write(chat_message)

# Input from user
user_input = st.text_input("Your Query", key="user_input")

# Option for User Anonymity
anonymous_option = st.checkbox("Keep my identity and information anonymous")

# Image upload option (clearly marked as optional)
st.subheader("Upload an Image (Optional)")
st.text("If you have an image related to the incident, you can upload it here. This step is optional.")
uploaded_image = st.file_uploader("", type=["jpg", "png", "jpeg"])

if user_input:
    st.session_state.chat_history.append(message(user_input, is_user=True))

    try:
        if uploaded_image is not None:
            if save_uploaded_file(uploaded_image):
                st.success("Image successfully saved.")
            else:
                st.error("Failed to save image.")

        result = analyze_query(user_input, "", "")
        st.session_state.chat_history.append(message(result))

        intent_classification = None
        location = None
        other_details = None

        for line in result.split("\n"):
            if "Intent Classification:" in line:
                intent_classification = line.split(": ")[-1].strip()

        # Write data to CSV file
        csv_filename = "anonymous_data.csv" if anonymous_option else "user_data.csv"
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "", "", user_input,
                intent_classification, location, other_details
            ])
        st.success("Data successfully saved to CSV file.")

        # If an intent classification is present, display follow-up questions
        if intent_classification and intent_classification in follow_up_questions:
            follow_up_responses = display_follow_up_questions(intent_classification)

            # Write follow-up data to CSV file
            if follow_up_responses:
                with open(csv_filename, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        "", "", user_input,
                        intent_classification,
                        *follow_up_responses.values()
                    ])
                st.success("Follow-up data successfully saved to CSV file.")
                st.success("Thank you for providing the necessary details. We will look into the matter and take appropriate action.")

            else:
                st.success("Thank you for reaching out. We appreciate you reporting this incident.")
    except ValueError as e:
        st.error(e)

