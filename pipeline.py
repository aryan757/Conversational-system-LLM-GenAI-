import streamlit as st
import requests
import json

def make_api_request(api_key, query):
    headers = {
        'Content-Type': 'application/json',
        'Apikey': f'Api-Key {api_key}', 
    }

    data = {
        "payload": query
    }

    url = 'https://payload.vextapp.com/hook/IB365S9NWF/catch/$(channel_token)'  # Update this URL with your endpoint

    response = requests.post(url, json=data, headers=headers)
    return response.text

def main():
    st.title("Interactive API Query")

    api_key = "hAkKkUQN.TEh8Lk8z3gL6RqXu58tduOfaCKhrMd0z"
    query = st.text_input("Enter your query:")

    if st.button("Submit"):
        if query:
            try:
                response_text = make_api_request(api_key, query)
                output = json.loads(response_text)
                st.success("API Response:")
                print(output["text"])
                st.code(output["text"])
            except Exception as e:
                st.error(f"Error occurred: {e}")
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()
