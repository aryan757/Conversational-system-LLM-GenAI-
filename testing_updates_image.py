import streamlit as st
import csv
from transformers import pipeline
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
import geocoder
from dotenv import load_dotenv
import base64

load_dotenv()

# Function to perform sentiment analysis and incident classification
def analyze_query(user_query, user_location, user_name, user_phone):
    # Access the Hugging Face API token from the environment variable
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
        1. Determine the most appropriate category for the incident based on the sentiment and content of the user query.
        2. Identify and extract entities such as location, time, or individuals involved.

        User Name: "{user_name}"
        User Phone: "{user_phone}"
        User Query: "{user_query}"
        User Location: "{user_location}"

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
    result = chain.run(user_query=user_query, user_location=user_location, user_name=user_name, user_phone=user_phone)  # Pass user_name and user_phone here
    return result

# Function to perform image-to-text conversion
def perform_image_to_text(image_url):
    image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
    return image_to_text(image_url)

# Streamlit front-end
st.title("Police सेवा portal System .")

# Input from user
user_name = st.text_input("User Name")
user_phone = st.text_input("User Phone")
user_query = st.text_area("Your Query")
uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# Fetch and display the user's current location
location_details = geocoder.ip('me').latlng if geocoder.ip('me').latlng is not None else None

if st.button("Analyze Query"):
    if user_query:
        user_location = f"{location_details[0]}, {location_details[1]}" if location_details else None
        # Call the function to analyze the query with the user's location
        try:
            result = analyze_query(user_query, user_location, user_name, user_phone)
            # Display the results
            st.subheader("Analysis Results:")
            intent_classification = None
            location = None
            other_details = None
            for line in result.split("\n"):
                if "Intent Classification:" in line:
                    intent_classification = line.split(": ")[-1]
                elif "Location:" in line:
                    location = line.split(": ")[-1]
                elif "Other Details:" in line:
                    other_details = line.split(": ")[-1]
            st.write("- Intent Classification:", intent_classification)
            st.write("  - Location:", location)
            st.write("  - Other Details:", other_details)
            
            # Write data to CSV file
            with open('user_data.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user_name, user_phone, user_query, intent_classification, other_details])
                
            st.success("Data successfully saved to CSV file.")
            
        except ValueError as e:
            st.error(e)
    else:
        st.error("Please enter your query.")

if uploaded_image is not None:
    st.image(uploaded_image, caption='Uploaded Image')
    image_url = "data:image/png;base64," + base64.b64encode(uploaded_image.read()).decode("utf-8")
    image_text = perform_image_to_text(image_url)
    st.subheader("Image-to-Text Conversion:")
    st.write(image_text)
