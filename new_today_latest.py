import streamlit as st
import csv
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

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
        current_index = st.session_state['current_question_index']
        
        if current_index < len(questions):
            question = questions[current_index]
            st.session_state['follow_up_responses'][question] = st.text_input(question)
            
            if st.button("Next"):
                st.session_state['current_question_index'] += 1
                st.experimental_rerun()
            
            if st.button("Skip"):
                st.session_state['current_question_index'] += 1
                st.experimental_rerun()
                
        else:
            st.success("All follow-up questions answered.")
    else:
        st.warning("No follow-up questions for the given intent classification.")
        return {}


# Streamlit front-end
st.title("Police सेवा portal System.")

# Input from user
user_name = st.text_input("User Name (Optional)")
user_phone = st.text_input("User Phone (Optional)")
user_query = st.text_area("Your Query")

# Image upload option (clearly marked as optional)
st.subheader("Upload an Image (Optional)")
st.text("If you have an image related to the incident, you can upload it here. This step is optional.")
uploaded_image = st.file_uploader("", type=["jpg", "png", "jpeg"])

# Option for User Anonymity
anonymous_option = st.checkbox("Keep my identity and information anonymous")

# Analyze Query button
if st.button("Analyze Query"):
    if user_query:
        try:
            if uploaded_image is not None:
                if save_uploaded_file(uploaded_image):
                    st.success("Image successfully saved.")
                else:
                    st.error("Failed to save image.")
            csv_filename = "anonymous_data.csv" if anonymous_option else "user_data.csv"
            result = analyze_query(user_query, user_name, user_phone)
            st.subheader("Analysis Results:")
            intent_classification = None
            location = None
            other_details = None

            for line in result.split("\n"):
                if "Intent Classification:" in line:
                    intent_classification = line.split(": ")[-1].strip()
                    st.write("- Intent Classification:", intent_classification)
               # elif "Location:" in line:
                #    st.write("  - Location:", location)
               # elif "Other Details:" in line:
                #    other_details = line.split(": ")[-1]
                #    st.write("  - Other Details:", other_details)

            # Write data to CSV file
            with open(csv_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    user_name, user_phone, user_query,
                    intent_classification, location, other_details
                ])
                
            st.success("Data successfully saved to CSV file.")
            
            # If an intent classification is present, display follow-up questions
            if intent_classification and intent_classification in follow_up_questions:
                st.session_state['intent_classification'] = intent_classification
                st.session_state['follow_up_responses'] = {question: "" for question in follow_up_questions[intent_classification]}
                st.session_state['current_question_index'] = 0  # Reset the question index
        except ValueError as e:
            st.error(e)

# If follow-up questions need to be displayed, create input fields for them one by one
if 'intent_classification' in st.session_state and st.session_state['intent_classification'] in follow_up_questions:
    display_follow_up_questions(st.session_state['intent_classification'])

if st.button("Submit Follow-up Information"):
    # Handle the submission of follow-up information
    csv_filename = "anonymous_data.csv" if anonymous_option else "user_data.csv"
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            user_name, user_phone, user_query,
            st.session_state['intent_classification'],
            *st.session_state['follow_up_responses'].values()
        ])
    st.success("Follow-up data successfully saved to CSV file.")
    # Clear the session state after successful submission
    del st.session_state['intent_classification']
    del st.session_state['follow_up_responses']
    st.session_state['current_question_index'] = 0
