import streamlit as st
from streamlit_chat import message
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

# Define follow-up questions for each intent classification
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
    # Add more intent classifications and their respective follow-up questions
}

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.follow_up_index = 0
    st.session_state.user_responses = []
    st.session_state.intent_classification = None

# Function to analyze the user query and classify the intent
def analyze_query(user_query):
    api_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
    if not api_token:
        raise ValueError("Hugging Face API token not found in environment variables.")

    prompt_template = """
    Analyze the sentiment and content of the following "{user_query}". Classify the incident into one of the specified categories:

    Categories:
    - Cyber crime incident
    - Child safety
    - Other categories...

    Instructions:
    1. Determine the most appropriate category for the incident based on the sentiment and content of the user query.


    Response Format:

        Intent Classification:

    """

    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = LLMChain(
        llm=HuggingFaceHub(repo_id='mistralai/Mistral-7B-Instruct-v0.2', model_kwargs={'temperature': 0.1, 'max_new_tokens': 250}),
        prompt=prompt
    )
    result = chain.run(user_query=user_query)
    intent_classification = result.split(": ")[-1].strip()
    return intent_classification

# Streamlit front-end
st.title("Chatbot System")

# Display greeting message
if not st.session_state.chat_history:
    st.session_state.chat_history.append(message("Hello! I'm a chatbot. Let's have a conversation.", is_user=False))

# Display chat history
for chat_message in st.session_state.chat_history:
    st.write(chat_message)

# Get user query and classify intent
user_query = st.text_input("You:", key="user_query")

if user_query:
    st.session_state.chat_history.append(message(user_query, is_user=True))

    try:
        intent_classification = analyze_query(user_query)
        st.session_state.intent_classification = intent_classification
        st.session_state.chat_history.append(message(f"Intent Classification: {intent_classification}", is_user=False))

        # Display follow-up questions after intent classification
        if st.session_state.intent_classification in follow_up_questions:
            questions = follow_up_questions[st.session_state.intent_classification]

            # Reset follow-up index if a new intent is classified
            if st.session_state.follow_up_index >= len(questions):
                st.session_state.follow_up_index = 0
                st.session_state.user_responses = []

            if st.session_state.follow_up_index < len(questions):
                question = questions[st.session_state.follow_up_index]
                st.write(f"Bot: {question}")
                user_response = st.text_input("You:", key=f"follow_up_{st.session_state.follow_up_index}")

                if user_response:
                    st.session_state.chat_history.append(message(user_response, is_user=True))
                    st.session_state.user_responses.append(user_response)
                    st.session_state.follow_up_index += 1

                    # Check if there are more questions to ask and rerun for next question
                    if st.session_state.follow_up_index < len(questions):
                        st.experimental_rerun()
                    else:
                        st.success("Thank you for providing the necessary details.")
                        st.write("Here are your responses:")
                        for i, response in enumerate(st.session_state.user_responses):
                            st.write(f"{i + 1}. {response}")
                        st.write("Have a great day!")
                        # Reset follow-up index and user responses for the next conversation
                        st.session_state.follow_up_index = 0
                        st.session_state.user_responses = []

    except ValueError as e:
        st.error(e)

else:
    if st.session_state.intent_classification is None:
        # This message should only appear if no intent has been classified yet
        st.write("Bot: I'm sorry, I couldn't classify your query into any known category. Please try rephrasing your concern.")