import streamlit as st
from transformers import AutoTokenizer, BartForConditionalGeneration

# Initialize the model and tokenizer
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

# Streamlit page title
st.title('Text Summarization with BART')

# Text area for user input
user_input = st.text_area("Enter text to summarize", height=200)

# Summarization button
if st.button('Summarize'):
    if user_input:
        # Tokenize the user input
        inputs = tokenizer([user_input], max_length=1024, return_tensors="pt")
        
        # Generate summary
        summary_ids = model.generate(inputs["input_ids"], num_beams=4, min_length=25, max_length=100)
        
        # Decode the summary
        summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        
        # Display the summary
        st.subheader('Summary')
        st.write(summary)
    else:
        st.write("Please enter some text to summarize.")