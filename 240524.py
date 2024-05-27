import streamlit as st
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
import geocoder
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static
from geopy.exc import GeocoderTimedOut


load_dotenv()

# Ensure the 'uploaded_images' directory exists
os.makedirs("uploaded_images", exist_ok=True)


def set_background_image(url):
    """Sets a background image for the Streamlit app."""
    css_style = f"""
    <style>
    .stApp {{
        background-image: url("{url}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)


# Follow-up questions
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
    "issue recorded": [
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


# Function to analyze query
def analyze_query(user_query, user_location, user_name="", user_phone=""):
    # Access Hugging Face API token from environment variable
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
        1. Determine the most appropriate category for the incident based on the sentiment and content of the user query, if failed to classify then give the response as "issue recorded".
         2. Extract relevant entities from the user query, including location (if possible).


        User Query: "{user_query}"
        """
    repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
    llm = LLMChain(HuggingFaceHub(api_token=api_token, repo_id=repo_id))
    analysis = llm.run(prompt_template)

    # Extract intent classification and location (if present)
    intent = analysis["classification"][0]["label"]
    location = analysis.get("extracted_location", user_location)

    # Generate response based on intent
    if intent == "X":
        response = "I couldn't understand the nature of your incident. Please try rephrasing your query or providing more details."
    else:
        response = f"The nature of your incident seems to be related to {intent}.  Would you like to provide more details?"

    return intent, location, response



# Chatbot conversation flow
st.title("Police Seva Portal Chatbot")

# Set background image (optional)
# set_background_image("[Image URL]")

st.write("Hello, how may I help you?")

user_name = st.text_input("Name (Optional)", key="user_name")
user_phone = st.text_input("Phone Number (Optional)", key="user_phone")

user_query = st.text_area("What is your query?", key="user_query")

if st.button("Submit Query"):
    if not user_query:
        st.error("Please enter your query.")
    # Get user location (optional)
    user_location = ""
    get_location = st.checkbox("Share your current location", key="get_location")
    if get_location:
        try:
            g = geocoder.ip('me')
            user_location = g.latlng
        except (geocoder.GeocoderTimedOut, geocoder.GeocoderUnavailable):
            st.error("Unable to get your location. Please try again later.")

    # Analyze user query
    intent, location, response = analyze_query(user_query, user_location, user_name, user_phone)
    st.write(response)

    # Display follow-up questions based on intent (if applicable)
    if intent in follow_up_questions:
        follow_up_data = {}
        for question in follow_up_questions[intent]:
            skip = st.checkbox(f"{question} (Optional)", key=question)
            if not skip:
                answer = st.text_input(question, key=question+"_answer")
                follow_up_data[question] = answer

        if st.button("Submit Follow-up Information"):
            # Save data to CSV file (replace with your preferred backend storage)
            data = {
                "Name": user_name,
                "Phone": user_phone,
                "Query": user_query,
                "Intent": intent,
                "Location": location,
                **follow_up_data
            }
            df = pd.DataFrame(data, index=[0])
            try:
                df.to_csv("incident_data.csv", mode='a', header=not os.path.exists("incident_data.csv"))
                st.success("Thank you for contacting the Police Seva Portal. Your information has been recorded.")
            except Exception as e:
                st.error(f"An error occurred while saving data: {e}")
