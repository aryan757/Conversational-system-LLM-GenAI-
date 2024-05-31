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
    st.session_state.follow_up_index = 0
    st.session_state.follow_up_responses = {}
    st.session_state.intent_classification = None
    st.session_state.current_question = ""
    st.session_state.loading = False

# Define follow-up questions with all lowercase keys
follow_up_questions = {
    "child safety": [
        "Child's name",
        "Child's age",
        "Description of clothing last worn",
        "Last known location and time",
        "Any known associates or suspects"
    ],
    "cyber crime incident": [
        "Type of cyber crime",
        "Description of the incident",
        "Date and time of the incident",
        "Any known suspects or source of the attack",
        "Account number (if bank involved)(Optional)",
        "Bank details (Name,Branch,IFSC code.)(Optional)"
    ],
    "women help desk": [
        "Nature of the incident",
        "Time and location of the incident",
        "Description of the perpetrator",
        "Immediate support needed",
        "Any witnesses or evidence available"
    ],
    "public healthcare": [
        "Type of health concern",
        "Number of people affected",
        "Location of the healthcare issue",
        "Urgency of the situation",
        "Availability of medical assistance"
    ],
    "road accident": [
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
    "fire accident": [
        "Location of the fire",
        "Time the fire started",
        "Known cause of the fire",
        "Injuries or fatalities",
        "Current status of the fire"
    ],
    "issue recorded": [
        "Description of the incident",
        "Timing",
        "Help needed (Yes/No)",
        "Current location"
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
        - cyber crime incident
        - women help desk
        - public healthcare
        - fire accident
        - road accident
        - child safety
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
    intent_classification = intent_classification.lower()

    if intent_classification in follow_up_questions:
        questions = follow_up_questions[intent_classification]

        if st.session_state.follow_up_index < len(questions):
            question = questions[st.session_state.follow_up_index]
            
            if st.session_state.current_question != question:
                st.session_state.current_question = question
                st.session_state.chat_history.append({"role": "bot", "content": question})

            for chat_message in st.session_state.chat_history:
                display_message(chat_message)

            user_input = st.text_input("You:", key=f"follow_up_{intent_classification}_{question}")
            skip_question = st.button("Skip", key=f"skip_{intent_classification}_{question}")

            if user_input or skip_question:
                response = user_input if user_input else "Skipped"
                st.session_state.follow_up_responses[question] = response
                st.session_state.chat_history.append({"role": "user", "content": response})
                st.session_state.follow_up_index += 1
                st.session_state.current_question = ""
                st.experimental_rerun()

        if st.session_state.follow_up_index == len(questions):
            return st.session_state.follow_up_responses
    else:
        st.warning("No follow-up questions for the given intent classification.")
        return {}

def display_message(chat_message):
    role = chat_message["role"]
    content = chat_message["content"]

    if role == "user":
        st.markdown(f"<div style='text-align: right;'><b>You:</b> {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left;'><b>🤖:</b> {content}</div>", unsafe_allow_html=True)

# Streamlit front-end
st.title("Police सेवा Portal System (Conversational)")

# Display greeting message only if chat history is empty
if not st.session_state.chat_history:
    st.session_state.chat_history.append({"role": "bot", "content": "Hello! Welcome to the Police सेवा Portal System. How can I assist you today?"})

# Display chat history
for chat_message in st.session_state.chat_history:
    display_message(chat_message)

# Input from user
user_input = st.text_input("You:", key="user_input")

# Option for User Anonymity
anonymous_option = st.checkbox("Keep my identity and information anonymous")
with st.sidebar:
    st.subheader("Upload an Image (Optional)")
    st.text("If you have an image related to the incident, you can upload it here. This step is optional.")
    uploaded_image = st.file_uploader("", type=["jpg", "png", "jpeg"])

if user_input and not st.session_state.get('intent_classification'):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.loading = True

    try:
        if uploaded_image is not None:
            if save_uploaded_file(uploaded_image):
                st.success("Image successfully saved.")
            else:
                st.error("Failed to save image.")

        # Display loading GIF
        loading_gif = "gear.gif"  # Replace with your loading GIF file path
        st.image(loading_gif)

        result = analyze_query(user_input, "", "")
        
        intent_classification = None
        location = None
        other_details = None

        for line in result.split("\n"):
            if "Intent Classification:" in line:
                intent_classification = line.split(": ")[-1].strip().lower()
            elif "Location:" in line:
                location = line.split(": ")[-1].strip()
            elif "Other Details:" in line:
                other_details = line.split(": ")[-1].strip()
        
        response_message = f"Intent Classification: {intent_classification}\nLocation: {location}\nOther Details: {other_details}"
        st.session_state.chat_history.append({"role": "bot", "content": response_message})

        # Store the extracted details in session state
        st.session_state.intent_classification = intent_classification
        st.session_state.location = location
        st.session_state.other_details = other_details

        # Prepare CSV row data
        csv_row = [
            "", "", user_input,
            st.session_state.intent_classification or "",
            st.session_state.location or "",
            st.session_state.other_details or ""
        ]

        # Write data to CSV file
        csv_filename = "anonymous_data.csv" if anonymous_option else "user_data.csv"
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(csv_row)
        st.success("Data successfully saved to CSV file.")

        # If an intent classification is present, start displaying follow-up questions
        if st.session_state.intent_classification and st.session_state.intent_classification in follow_up_questions:
            display_follow_up_questions(st.session_state.intent_classification)

        st.session_state.loading = False

    except ValueError as e:
        st.session_state.loading = False
        st.error(e)
elif st.session_state.get('intent_classification') and st.session_state.follow_up_index < len(follow_up_questions[st.session_state.intent_classification]):
    # Continue asking follow-up questions
    display_follow_up_questions(st.session_state.intent_classification)
elif st.session_state.get('intent_classification') and st.session_state.follow_up_index >= len(follow_up_questions[st.session_state.intent_classification]):
    # All follow-up questions have been answered
    follow_up_responses = st.session_state.follow_up_responses
    # Prepare follow-up CSV row data
    follow_up_csv_row = [
        "", "", user_input,
        st.session_state.intent_classification or "",
        *follow_up_responses.values()
    ]
    # Write follow-up data to CSV file
    csv_filename = "anonymous_data.csv" if anonymous_option else "user_data.csv"
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(follow_up_csv_row)
    st.success("Follow-up data successfully saved to CSV file.")
    st.success("Thank you for providing the necessary details. We will look into the matter and take appropriate action.")
    # Reset follow-up state for the next conversation
    st.session_state.follow_up_index = 0
    st.session_state.follow_up_responses = {}
    st.session_state.intent_classification = None
else:
    st.success("Thank you for reaching out. We appreciate you reporting this incident.")
