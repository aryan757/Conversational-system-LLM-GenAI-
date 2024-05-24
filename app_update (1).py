import streamlit as st
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
import geocoder
from dotenv import load_dotenv

load_dotenv()

# Function to perform sentiment analysis and incident classification
def analyze_query(user_query, user_location):
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
    #result = chain.run(user_query=user_query)
    #return result.split("\n")
    result = chain.run(user_query=user_query, user_location=user_location)  # Pass user_location here
    return result.split("\n")

# Function to get the current location name and coordinates
def get_current_location_details():
    g = geocoder.ip('me')
    if g.latlng is not None:
        reverse = geocoder.osm(g.latlng, method='reverse')
        if reverse.ok:
            return {
                'coordinates': g.latlng,
                'address': reverse.address
            }
        else:
            return {
                'coordinates': g.latlng,
                'address': None
            }
    else:
        return None
    



def append_to_csv(file_name, data):
    import csv
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)



# Streamlit front-end
st.title("Police सेवा portal System for ನಮ್ಮ ಬೆಂಗಳೂರು")
logo_url = "https://bcp.karnataka.gov.in/uploads/dept_logo1648209532.png"
st.image(logo_url, caption='Police Department Logo')

# Input from user
user_name = st.text_input("User Name")
user_query = st.text_area("Your Query")

# Fetch and display the user's current location
location_details = get_current_location_details()
if location_details:
    st.write(f"Your current GPS coordinates are: {location_details['coordinates']}")
    st.write(f"Your approximate location is: {location_details['address']}")
else:
    st.error("Unable to retrieve your GPS coordinates.")

if st.button("Analyze Query"):
    if user_query and location_details:
        user_location = f"{location_details['coordinates'][0]}, {location_details['coordinates'][1]}"
        # Call the function to analyze the query with the user's location
        try:
            result = analyze_query(user_query, user_location)
            # Display the results
            st.subheader("Analysis Results:")
            analysis_results = []
            for line in result:
                st.write(line)
                analysis_results.append(line.split(": ")[-1])  # Extract the result details
            if analysis_results:
                # Append the results to a CSV file
                csv_data = [user_name, location_details['address']] + analysis_results
                append_to_csv('user_queries.csv', csv_data)
                st.success("Data successfully saved to CSV file.")
        except ValueError as e:
            st.error(e)
    else:
        st.error("Please enter your query.")